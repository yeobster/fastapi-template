from typing import List, TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship

from models.base import ModelBase
from models.mixin import UNIQUE, DatetimeMixIn

if TYPE_CHECKING:
    from models.user import User


class UserGroupBase(SQLModel):
    name: str = Field(max_length=30, sa_column_kwargs=UNIQUE, index=True)
    desc: Optional[str] = Field(None, max_length=255)


class UserGroupCreate(UserGroupBase):
    """생성 객체"""

    pass


class UserGroupUpdate(UserGroupBase):
    """업데이트 객첵"""

    pass


class UserGroupPublicRead(SQLModel):
    """공개 정보"""

    id: int
    name: str


class UserGroupPrivateRead(UserGroupPublicRead, DatetimeMixIn):
    """개인 정보"""


class UserGroup(
    DatetimeMixIn,
    UserGroupBase,
    ModelBase,
    table=True,
):
    """
    DB model

    Args:
        ModelBase ([type]): [description]
        UserGroupBase ([type]): [description]
        table (bool, optional): [description]. Defaults to True.
    """

    members: List["User"] = Relationship(back_populates="user_group")
