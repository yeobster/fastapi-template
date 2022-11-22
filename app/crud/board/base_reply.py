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
from sqlmodel import Session, SQLModel, select, func

# core
from models.base import ModelBase
from schemas.res import RemoveRowResult

import utils

ModelType = TypeVar("ModelType", bound=ModelBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BoardReplyCRUDBase(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: Type[ModelType]):
        """
        BoardReplyCRUDBase object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A ModelBase class: table=true
        * `schema`: A SQLModel model class
        """
        self.model = model

    def create(
        self,
        db: Session,
        obj_in: CreateSchemaType,
        post_id: int,
        writer_id: int,
    ):
        now = utils._datetime.get_current_linux_timestamp()
        jsonable = obj_in.dict()
        db_obj = self.model(
            **jsonable,
            writer_id=writer_id,
            post_id=post_id,
            created_at=now,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get(self, db: Session, _id: Any) -> Optional[ModelType]:
        r = db.get(self.model, _id)
        return r

    def get_multi(self, db: Session, post_id: int) -> List[ModelType]:
        stmt = select(self.model).where(self.model.post_id == post_id)
        r = db.exec(stmt).all()
        return r

    def get_count(self, db: Session):
        stmt = select(func.count(self.model.id))
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

        # commit
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def remove(self, db: Session, obj_in: ModelType) -> RemoveRowResult:
        db.delete(obj_in)
        db.commit()
        r = RemoveRowResult(id=obj_in.id)
        return r
