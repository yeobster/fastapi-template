from typing import Optional, List, TypeVar, TypedDict, Type
from pydantic import BaseModel
from sqlmodel import SQLModel

# _T = Type("_T")

PostListResponseType = TypeVar("PostListResponseType", bound=SQLModel)


class BoardPublicReadResponse(BaseModel):
    posts: Optional[List[PostListResponseType]]
    all_post_count: Optional[int]
