from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlmodel import Session, SQLModel, select, func


import schemas
from schemas.res import RemoveRowResult
from models.base import ModelBase
from utils import _datetime

ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, _id: Any) -> Optional[ModelType]:
        r = db.get(self.model, _id)
        return r

    def get_by_name(self, db: Session, name: Any) -> Optional[ModelType]:

        # check name attribute
        if not hasattr(self.model, "name"):
            raise Exception("Not found status in self.model")

        stmt = select(self.model).where(self.model.name == name)
        r = db.exec(stmt).first()
        return r

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        r = db.exec(stmt).all()
        return r

    def get_multi_desc(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        stmt = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.id.desc())
        )
        r = db.exec(stmt).all()
        return r

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        jsonable = obj_in.dict()
        db_obj = self.model(**jsonable)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        jsonable = db_obj.dict()

        # Dict인지 체크
        if isinstance(obj_in, Dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_none=True)

        # set update data
        for field in jsonable:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def replace(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:

        # check dict
        if isinstance(obj_in, Dict):
            new_data = obj_in
        else:
            new_data = obj_in.dict()

        # set new data
        for k, _ in db_obj.dict().items():
            if k == "id":
                continue
            setattr(db_obj, k, new_data[k])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, _id: int) -> ModelType:
        obj = db.get(self.model, _id)
        db.delete(obj)
        db.commit()
        r = RemoveRowResult(id=obj.id)
        return r

    def activate(
        self,
        db: Session,
        *,
        _id: int,
    ) -> ModelType:
        """
        활성화
        """
        # check id

        obj = self.get(db, _id=_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        # check status
        if not hasattr(self.model, "status"):
            raise Exception("Not found status in self.model")

        updated_at = _datetime.get_current_linux_timestamp()
        obj.updated_at = updated_at
        obj.status = schemas.Status.active

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def deactivate(
        self,
        db: Session,
        *,
        _id: int = None,
    ) -> ModelType:
        """
        비활성화
        """
        if not hasattr(self.model, "status"):
            raise Exception("Not found status in model")

        obj = self.get(db, _id=_id)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        updated_at = _datetime.get_current_linux_timestamp()
        obj.updated_at = updated_at
        obj.status = schemas.Status.inactive

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def set_temporary(
        self,
        db: Session,
        *,
        _id: int = None,
    ) -> ModelType:
        """
        임시
        """
        # check status
        if not hasattr(self.model, "status"):
            raise Exception("Not found status in model")

        obj = self.get(db, _id=_id)
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        updated_at = _datetime.get_current_linux_timestamp()
        obj.updated_at = updated_at
        obj.status = schemas.Status.temporary

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def get_count(self, db: Session) -> int:
        stmt = select(func.count(self.model.id))
        r = db.exec(stmt).one()
        return r
