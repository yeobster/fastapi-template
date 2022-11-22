from pydantic import EmailStr
from typing import List, Optional
from sqlmodel import Relationship, Field, SQLModel

# models
from models.base import ModelBase
from models.boards.base import BoardPublicReadResponse
from models.mixin import (
    PostMixIn,
    DatetimeMixIn,
    PostMetaMixIn,
    AttachmentGroupMixin,
    CorpMixIn,
)

### models ###
from models.user import UserPublicRead
from models.user import User


class BoardQaBase(PostMixIn, AttachmentGroupMixin, CorpMixIn):
    email: Optional[EmailStr] = Field(None, title="이메일")
    phone: Optional[str] = Field(None, max_length=20, title="연락처")


class BoardQaCreate(BoardQaBase):
    """생성 객체"""

    pass


class BoardQaUpdate(BoardQaBase):
    """업데이트 객체"""

    pass


# 주의: 마지막 파라메터부터 컬럼이 생성됨
class BoardQa(
    DatetimeMixIn,
    PostMetaMixIn,
    BoardQaBase,
    ModelBase,
    table=True,
):
    """
    BoardQa Table
    """

    ### foreign key ##

    # 게시물 제작자
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="qa_posts")

    ### relationship ###

    # 댓글리스트
    replies: List["BoardQaReply"] = Relationship(back_populates="board")


class BoardQaReplyBase(SQLModel):

    contents: str = Field(max_length=255)  # 댓글 내용


class BoardQaReplyCreate(BoardQaReplyBase):
    pass


class BoardQaReplyUpdate(BoardQaReplyBase):
    pass


class BoardQaReplyRead(BoardQaReplyBase):
    id: int
    writer_id: int
    writer: UserPublicRead


class BoardQaReply(BoardQaReplyBase, DatetimeMixIn, ModelBase, table=True):
    """
    댓글
    """

    ### foreign key ###
    # 자유게시판
    post_id: int = Field(foreign_key="board_qa.id")
    board: BoardQa = Relationship(back_populates="replies")

    # 댓글 작성자
    writer_id: int = Field(foreign_key="user.id")
    writer: User = Relationship(back_populates="qa_replies")


class BoardQaPublicReadShort(BoardQaBase, DatetimeMixIn, PostMetaMixIn):
    """공개 정보"""

    id: int
    author_id: int
    author: UserPublicRead
    replies_count: int = 0


class BoardQaPublicRead(BoardQaPublicReadShort):
    """공개 정보 리플포함"""

    replies: Optional[List[BoardQaReplyRead]]


class BoardQaPrivateRead(BoardQaPublicRead):
    """비공개 정보"""

    pass


class BoardQaPublicReadResponse(BoardPublicReadResponse):
    posts: Optional[List[BoardQaPublicRead]]
