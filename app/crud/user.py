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
from models.user import User as Model
from models.user import UserCreate as CreateModel
from models.user import UserUpdate as UpdateModel

from core.config import settings
import utils
import schemas

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

    def signup(self, db: Session, *, obj_in: CreateModel) -> Model:
        """
        override create
        """

        now = utils._datetime.get_current_linux_timestamp()
        at = {"created_at": now}

        # secret must be unicode or bytes
        if obj_in.password is not None:
            hashed_password = get_password_hash(obj_in.password)
            obj_in.password = hashed_password

        if obj_in.agree_private is True and obj_in.agree_terms is True:
            at["agreed_at"] = now

        # 가입시 게스트로 가입됨
        obj = Model(
            **obj_in.dict(), **at, user_group_id=schemas.UserGroup.guest["id"]
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
        user = self.get_by_email(db, email=email)

        # not found email
        if not user:
            return None

        # password와 db에 저장된 hashed password를 비교
        verified = verify_password(password, user.password)

        # check password
        if not verified:
            return None

        return user

    def create_temporary_password(
        self, db: Session, *, email: str
    ) -> Optional[Model]:
        """
        이메일로 정보를 불러온다.
        """

        # 등록된 이메일이 있는지 체크
        user = self.get_by_email(db=db, email=email)

        if user is None:
            return

        # 임시 비밀번호 생성하기
        temp_pass = utils._random.get_string(4, 4)

        # 임시 비밀번호 암호화 하기
        hashed_password = get_password_hash(temp_pass)
        user.password = hashed_password

        # db 저장
        db.add(user)
        db.commit()
        db.refresh(user)

        # sendgrid가 세팅되어 있다면 이메일 보내기
        if settings.SENDGRID_CHECKING is not None:
            _mailer.password.send_temp(email, temp_pass, type_string="유저")

        return user

    def authorize(
        self,
        db: Session,
        db_obj: Model,
    ):
        db_obj.is_authorized = True
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj


user = CRUD(Model)
