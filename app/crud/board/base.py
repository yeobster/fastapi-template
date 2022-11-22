from typing import (
    Generic,
    TypeVar,
    Type,
    Any,
    Optional,
    List,
    Union,
    Dict,
)
from sqlmodel import Session, SQLModel, and_, select, func, or_
from fastapi.exceptions import HTTPException
from fastapi import status

# core
from models.base import ModelBase
from schemas.status import Status
from schemas.res import RemoveRowResult
import utils

ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BoardCRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        BoardCRUDBase object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A ModelBase class: table=true
        * `schema`: A SQLModel model class
        """
        self.model = model

    def create(self, db: Session, obj_in: CreateSchemaType, author_id: int):
        now = utils._datetime.get_current_linux_timestamp()
        jsonable = obj_in.dict()
        db_obj = self.model(**jsonable, author_id=author_id, created_at=now)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, _id: Any) -> Optional[ModelType]:
        obj = db.get(self.model, _id)
        return obj

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        stmt = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id.desc())
        )
        r = db.exec(stmt).all()
        return r

    def get_count(self, db: Session) -> int:
        stmt = select(func.count(self.model.id))
        r = db.exec(stmt).one()
        return r

    def get_active_one(self, db: Session, _id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(
            and_(self.model.status == Status.active, self.model.id == _id)
        )
        obj = db.exec(stmt).one_or_none()

        return obj

    def get_active_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, author_id: int
    ) -> List[ModelType]:
        stmt = (
            select(self.model)
            .where(
                or_(
                    self.model.status == Status.active,
                    self.model.author_id == author_id,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        r = db.exec(stmt).all()
        return r

    def get_active_count(self, db: Session, author_id: int) -> int:
        stmt = select(func.count(self.model.id)).where(
            or_(
                self.model.status == Status.active,
                self.model.author_id == author_id,
            )
        )
        r = db.exec(stmt).one()
        return r

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:

        now = utils._datetime.get_current_linux_timestamp()
        jsonable = db_obj.dict()

        # dict로 변경
        if isinstance(obj_in, Dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_none=True)

        # set update data
        for field in jsonable:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        # set update date
        db_obj.updated_at = now

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def remove(self, db: Session, obj_in: ModelType) -> RemoveRowResult:
        db.delete(obj_in)
        db.commit()
        r = RemoveRowResult(id=obj_in.id)
        return r

    def set_status(
        self,
        db: Session,
        *,
        # _id: int,
        obj_in: ModelType,
        _status: Status,
    ) -> ModelType:
        """
        활성화
        """
        # check id
        _now = utils._datetime.get_current_linux_timestamp()
        # obj: ModelType = self.get(db, _id=_id)

        if not obj_in:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "게시물을 찾을 수 없습니다.")

        # check status
        if not hasattr(self.model, "status"):
            raise Exception("Not found status in self.model")

        obj_in.updated_at = _now
        obj_in.status = _status

        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)

        return obj_in

    def count_up(self, db: Session, _id: int):
        obj: ModelType = self.get(db, _id=_id)

        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "게시물을 찾을 수 없습니다.")

        # check status
        if not hasattr(self.model, "read_count"):
            raise Exception("Not found status in self.model")

        obj.read_count = obj.read_count + 1

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj
