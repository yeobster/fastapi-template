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
)

### models ###
from models.user import UserPublicRead
from models.user import User


class BoardNoticeBase(PostMixIn, AttachmentGroupMixin):
    pass


class BoardNoticeCreate(BoardNoticeBase):
    """생성 객체"""

    pass


class BoardNoticeUpdate(BoardNoticeBase):
    """업데이트 객체"""

    pass


# 주의: 마지막 파라메터부터 컬럼이 생성됨
class BoardNotice(
    DatetimeMixIn,
    PostMetaMixIn,
    BoardNoticeBase,
    ModelBase,
    table=True,
):
    """
    BoardNotice Table
    """

    ### foreign key ##

    # 게시물 제작자
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="notice_posts")

    ### relationship ###

    # 댓글리스트
    replies: List["BoardNoticeReply"] = Relationship(back_populates="board")


class BoardNoticeReplyBase(SQLModel):

    contents: str = Field(max_length=255)  # 댓글 내용


class BoardNoticeReplyCreate(BoardNoticeReplyBase):
    pass


class BoardNoticeReplyUpdate(BoardNoticeReplyBase):
    pass


class BoardNoticeReplyRead(BoardNoticeReplyBase):
    id: int
    writer_id: int
    writer: UserPublicRead


class BoardNoticeReply(
    BoardNoticeReplyBase, DatetimeMixIn, ModelBase, table=True
):
    """
    댓글
    """

    ### foreign key ###
    # 자유게시판
    post_id: int = Field(foreign_key="board_notice.id")
    board: BoardNotice = Relationship(back_populates="replies")

    # 댓글 작성자
    writer_id: int = Field(foreign_key="user.id")
    writer: User = Relationship(back_populates="notice_replies")


class BoardNoticePublicReadShort(
    BoardNoticeBase, DatetimeMixIn, PostMetaMixIn
):
    """공개 정보"""

    id: int
    author_id: int
    author: UserPublicRead
    replies_count: int = 0


class BoardNoticePublicRead(BoardNoticePublicReadShort):
    """공개 정보 리플포함"""

    replies: Optional[List[BoardNoticeReplyRead]]


class BoardNoticePrivateRead(BoardNoticePublicRead):
    """비공개 정보"""

    pass


class BoardNoticePublicReadResponse(BoardPublicReadResponse):
    posts: Optional[List[BoardNoticePublicRead]]
