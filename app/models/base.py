# std
from typing import Optional, TypeVar, List
from pydantic import BaseModel

# third party
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.declarative import declared_attr
from utils import _string

ListResponseType = TypeVar("ListResponseType", bound=SQLModel)


class ModelBase(SQLModel):
    """
    SQLModel 기본 Model
    """

    id: Optional[int] = Field(default=None, primary_key=True, title="식별자")
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        return self._convert_table_name_to_snake_from_camel()

    @classmethod
    def _convert_table_name_to_snake_from_camel(cls) -> str:
        new_table_name = _string.convert_snakecase(cls.__name__)
        return new_table_name


class ReadListResponse(BaseModel):
    posts: Optional[List] = []
    all_post_count: Optional[int] = 0
