# TODO: 아래 기능은 검증되지 않음. 구현해야함.

# std
from typing import Any, Dict, Optional, Union, List
from sqlmodel import Session, select
from fastapi import status
from fastapi.exceptions import HTTPException

# core
from core.security import get_password_hash, verify_password
from core import _mailer
from crud.base import CRUDBase

# model
from models.superuser import Superuser as Model
from models.superuser import SuperuserCreate as CreateModel
from models.superuser import SuperuserUpdate as UpdateModel

import crud, utils
from core.config import settings
from schemas.status import Status


class CRUD(CRUDBase[Model, CreateModel, UpdateModel]):
    """
    User CRUD
    """

    def get_by_email(self, db: Session, *, email: str) -> Optional[Model]:
        """
        이메일로 정보를 불러온다.
        """

        # find user email address
        stmt = select(self.model).where(self.model.email == email)
        return db.exec(stmt).first()

    # def func(a, b="Hello", *args, c, **Kwargs)
    def signup(
        self, db: Session, *, obj_in: CreateModel, current_user: Model
    ) -> Model:
        """
        override create
        """

        now = utils._datetime.get_current_linux_timestamp()

        # secret must be unicode or bytes
        if obj_in.password is not None:
            hashed_password = get_password_hash(obj_in.password)
            obj_in.password = hashed_password

        obj = Model(
            **obj_in.dict(), created_at=now, created_user_id=current_user.id
        )

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Model,
        obj_in: Union[UpdateModel, Dict[str, Any]],
        is_set_updated_at=False,
    ) -> Model:
        """
        PUT, PATCH
        UserUpdate,
        """

        # 이메일 체크
        # 메일은 하나만 사용할 수 있다.
        if obj_in.email is not None and db_obj.email != obj_in.email:

            # 일반유저로 등록된 이메일이 있는지 체크한다.
            user = self.get_by_email(db, email=obj_in.email)
            if user is not None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=f"이미 일반유저 계정의 메일주소({obj_in.email})로 가입된 계정이 있습니다.",
                )

            # 관리자로 등록된 이메일이 있는지 체크한다.
            user = crud.superuser.get_by_email(db, email=obj_in.email)
            if user is not None:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail=f"이미 관리자 계정의 메일주소({obj_in.email})로 가입된 계정이 있습니다.",
                )

        if isinstance(obj_in, dict):
            # method PUT 해당
            updated = obj_in
        else:
            # method PATCH에 해당
            updated = obj_in.dict(exclude_none=True)

        # 비밀번호 인증
        if "password" in updated:
            if updated["password"]:

                # 암호화
                hashed_password = get_password_hash(updated["password"])
                updated["password"] = hashed_password

        # set update time
        if is_set_updated_at is True:
            updated_at = utils._datetime.get_current_linux_timestamp()
            updated["updated_at"] = updated_at

        r = super().update(db, db_obj=db_obj, obj_in=updated)

        return r

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        status: Optional[int] = None,
    ) -> List[Model]:

        stmt = select(self.model).limit(limit).offset(skip)
        if status is not None:
            stmt.where(self.model.status == Status.active)

        r = db.exec(stmt).all()

        return r

    # user 인증
    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[Model]:

        # check email.
        superuser = self.get_by_email(db, email=email)

        # not found email
        if not superuser:
            return None

        # password와 db에 저장된 hashed password를 비교
        verified = verify_password(password, superuser.password)

        # check password
        if not verified:
            return None

        return superuser

    def create_temporary_password(
        self, db: Session, *, email: str
    ) -> Optional[Model]:
        """
        이메일로 정보를 불러온다.
        """

        # 등록된 이메일이 있는지 체크
        superuser = self.get_by_email(db=db, email=email)

        if superuser is None:
            return

        # 임시 비밀번호 생성하기
        temp_pass = utils._random.get_string(4, 4)

        # 임시 비밀번호 암호화 하기
        hashed_password = get_password_hash(temp_pass)
        superuser.password = hashed_password

        # db 저장
        db.add(superuser)
        db.commit()
        db.refresh(superuser)

        if settings.SENDGRID_CHECKING is not None:
            type_string = "관리자"
            _mailer.password.send_temp(
                email=email, temp_pass=temp_pass, type_string=type_string
            )

        return superuser

    def authorize(self, db: Session, *, model: Model):
        model.is_authorized = True
        db.add(model)
        db.commit()
        db.refresh(model)

        return model


superuser = CRUD(Model)
