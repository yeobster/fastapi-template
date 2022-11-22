from typing import List, TYPE_CHECKING, Optional

from pydantic import EmailStr

# third party
from sqlmodel import Field, Relationship

# base model and mixins
from models.base import ModelBase
from models.mixin import (
    AccountMixIn,
    AccountPrivateMixIn,
    AuthorizationMixIn,
    DatetimeMixIn,
    AgreeMixIn,
    CorpMixIn,
)

# models
from models.usermeta import UserMeta
from models.usergroup import (
    UserGroupPublicRead,
    UserGroupPrivateRead,
    UserGroup,
)

if TYPE_CHECKING:
    from models.boards.faq import BoardFaq
    from models.boards.faq import BoardFaqReply
    from models.boards.notice import BoardNotice, BoardNoticeReply
    from models.boards.qa import BoardQa, BoardQaReply


class UserBase(AccountMixIn, CorpMixIn):
    pass


class UserCreate(UserBase, AccountPrivateMixIn, AgreeMixIn):
    """생성 객체"""

    pass


class UserUpdate(UserBase):
    """업데이트 객체"""

    email: Optional[EmailStr] = Field(
        None,
        description="이메일 주소는 관리자 계정과 사용자계정에서 중복사용 불가.",
    )
    nickname: Optional[str] = Field(max_length=60, title="별명")


class UserPublicRead(ModelBase):
    """공개 정보"""

    id: int
    nickname: str
    email: str
    photo: str
    user_group: UserGroupPublicRead


class UserPrivateRead(UserBase, DatetimeMixIn, AuthorizationMixIn, AgreeMixIn):
    """개인 정보"""

    id: int
    user_group_id: int
    user_group: UserGroupPrivateRead


class User(
    DatetimeMixIn,
    AgreeMixIn,
    AuthorizationMixIn,
    AccountPrivateMixIn,
    UserBase,
    ModelBase,
    table=True,
):
    """
    DB model

    Args:
        ModelBase ([type]): [description]
        UserBase ([type]): [description]
        table (bool, optional): [description]. Defaults to True.
    """

    user_group_id: int = Field(
        # default=schemas.UserGroup.guest["id"], foreign_key="user_group.id"
        foreign_key="user_group.id"
    )
    agreed_at: str = Field(None, max_length=13, title="동의한 날짜")

    # relationship
    user_group: UserGroup = Relationship(back_populates="members")
    user_meta: Optional[UserMeta] = Relationship(back_populates="user")

    #### 게시판 ###

    # FAQ
    faq_posts: Optional[List["BoardFaq"]] = Relationship(
        back_populates="author"
    )
    faq_replies: Optional[List["BoardFaqReply"]] = Relationship(
        back_populates="writer"
    )

    # 공지사항
    notice_posts: Optional[List["BoardNotice"]] = Relationship(
        back_populates="author"
    )
    notice_replies: Optional[List["BoardNoticeReply"]] = Relationship(
        back_populates="writer"
    )

    # QA
    qa_posts: Optional[List["BoardQa"]] = Relationship(back_populates="author")
    qa_replies: Optional[List["BoardQaReply"]] = Relationship(
        back_populates="writer"
    )
