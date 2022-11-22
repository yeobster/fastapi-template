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


class BoardFaqBase(PostMixIn, AttachmentGroupMixin):
    pass


class BoardFaqCreate(BoardFaqBase):
    """생성 객체"""

    pass


class BoardFaqUpdate(BoardFaqBase):
    """업데이트 객체"""

    pass


# 주의: 마지막 파라메터부터 컬럼이 생성됨
class BoardFaq(
    DatetimeMixIn,
    PostMetaMixIn,
    BoardFaqBase,
    ModelBase,
    table=True,
):
    """
    BoardFaq Table
    """

    ### foreign key ##

    # 게시물 제작자
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="faq_posts")

    ### relationship ###

    # 댓글리스트
    replies: List["BoardFaqReply"] = Relationship(back_populates="board")


class BoardFaqReplyBase(SQLModel):

    contents: str = Field(max_length=255)  # 댓글 내용


class BoardFaqReplyCreate(BoardFaqReplyBase):
    pass


class BoardFaqReplyUpdate(BoardFaqReplyBase):
    pass


class BoardFaqReplyRead(BoardFaqReplyBase):
    id: int
    writer_id: int
    writer: UserPublicRead


class BoardFaqReply(BoardFaqReplyBase, DatetimeMixIn, ModelBase, table=True):
    """
    댓글
    """

    ### foreign key ###
    # 자유게시판
    post_id: int = Field(foreign_key="board_faq.id")
    board: BoardFaq = Relationship(back_populates="replies")

    # 댓글 작성자
    writer_id: int = Field(foreign_key="user.id")
    writer: User = Relationship(back_populates="faq_replies")


class BoardFaqPublicReadShort(BoardFaqBase, DatetimeMixIn, PostMetaMixIn):
    """공개 정보"""

    id: int
    author_id: int
    author: UserPublicRead
    replies_count: int = 0


class BoardFaqPublicRead(BoardFaqPublicReadShort):
    """공개 정보 리플포함"""

    replies: Optional[List[BoardFaqReplyRead]]


class BoardFaqPrivateRead(BoardFaqPublicRead):
    """비공개 정보"""

    pass


class BoardFaqPublicReadResponse(BoardPublicReadResponse):
    posts: Optional[List[BoardFaqPublicRead]]
