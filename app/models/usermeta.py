from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, Field
from models.base import ModelBase

if TYPE_CHECKING:
    from models.user import User

from models.mixin import CorpMixIn


class UserMeta(
    ModelBase,
    table=True,
):
    """
    DB model

    Args:
        ModelBase ([type]): [description]
    """

    desc: Optional[str] = Field(None, max_length=255)  # 기타사항

    # sns
    facebook_url: Optional[str] = Field(None, max_length=255)
    facebook_token: Optional[str] = Field(None, max_length=255)

    twitter_url: Optional[str] = Field(None, max_length=255)
    instagram_url: Optional[str] = Field(None, max_length=255)
    youtube_url: Optional[str] = Field(None, max_length=255)
    github_url: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    medium_url: Optional[str] = Field(None, max_length=255)
    pinterest_url: Optional[str] = Field(None, max_length=255)
    behance_url: Optional[str] = Field(None, max_length=255)
    dribbble_url: Optional[str] = Field(None, max_length=255)

    ### relationship ###

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="user_meta")
