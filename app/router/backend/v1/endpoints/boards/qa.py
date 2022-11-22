from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

import models
import schemas

### post models ###

from models.boards.qa import BoardQa as _PostModel
from models.boards.qa import BoardQaCreate as _PostCreate
from models.boards.qa import BoardQaUpdate as _PostUpdate
from models.boards.qa import BoardQaPublicRead as _PostPublicRead
from models.boards.qa import BoardQaPrivateRead as _PostPrivateRead
from models.boards.qa import (
    BoardQaPublicReadShort as _PostPublicReadShort,
)
from models.boards.qa import BoardQaPublicReadResponse as _PostListResponse

### reply models ###
# from models.boards.qa import BoardQaReply as _Reply
from models.boards.qa import BoardQaReplyCreate as _ReplyCreate
from models.boards.qa import BoardQaReplyRead as _ReplyRead
from models.boards.qa import BoardQaReplyUpdate as _ReplyUpdate

# crud
from crud.board.qa import qa as board_crud
from crud.board.qa import qa_reply as reply_crud

# schemas
from router.backend import dependencies

router = APIRouter()

"""
create: admin
"""


@router.post("")
def write_post(
    obj_in: _PostCreate,
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(
        dependencies.get_current_active_user_in_admin_group
    ),
):
    """게시하기"""

    post = board_crud.create(db, obj_in=obj_in, author_id=current_user.id)
    return post


@router.get(
    "",
    response_model=_PostListResponse,
    response_model_exclude_none=True,
)
def get_post_list(
    db: Session = Depends(dependencies.get_session),
    skip: int = Query(1),
    limit: int = Query(10),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """게시글 리스트 불러오기"""

    res = _PostListResponse()
    res_posts: List[_PostPublicReadShort] = []
    _posts: List[_PostModel]

    # get posts
    # FIXME: 속도가 느려지면 count API를 신규로 추가하여 개발필요.
    if current_user.user_group_id == schemas.UserGroup.admin["id"]:
        # admin group인 경우 모든 게시물
        _posts = board_crud.get_multi(db, skip=skip, limit=limit)

        # set all post count in response
        _count = board_crud.get_count(db)
        res.all_post_count = _count

    else:
        # user일 경우 active한 게시물과 본인의 게시물
        _posts = board_crud.get_active_multi(
            db, author_id=current_user.id, skip=skip, limit=limit
        )

        # set all post count in response
        _count = board_crud.get_active_count(db, author_id=current_user.id)
        res.all_post_count = _count

    # set replies count
    for i in _posts:
        _len = len(i.replies)
        _obj = _PostPublicReadShort(
            **i.dict(), author=i.author, replies_count=_len
        )
        res_posts.append(_obj)

    # set posts in response
    res.posts = res_posts

    return res


@router.get(
    "/{post_id}",
    response_model=Union[_PostPublicRead, _PostPrivateRead],
    response_model_exclude_none=True,
)
def get_post_and_count_up(
    post_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """
    게시글 불러오기
    작성자가 아닐경우 read count up
    """

    post = board_crud.get(db, _id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # set replies count
    _len = len(post.replies)

    ### 작성자와 Superuser일 경우 ###
    if current_user.id == post.author_id or isinstance(
        current_user, models.Superuser
    ):
        return _PostPrivateRead(
            **post.dict(),
            author=post.author,
            replies=post.replies,
            replies_count=_len
        )

    ### 작성자가 아닌 일반유저일 경우 ###

    # active상태가 아니면 404
    if post.status != schemas.Status.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # make response.
    post = _PostPublicRead(
        **post.dict(),
        author=post.author,
        replies=post.replies,
        replies_count=_len
    )

    # update read count
    board_crud.count_up(db, _id=post_id)

    return post


@router.put(
    "/{post_id}",
    response_model_exclude_none=True,
)
def update_post(
    obj_in: _PostUpdate,
    post_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(
        dependencies.get_current_active_user_in_admin_group
    ),
):
    """게시물 수정"""

    # get reply
    post = board_crud.get(db, _id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다."
        )

    # author only
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="게시글 작성자가 아닙니다."
        )

    # update
    post = board_crud.update(db, db_obj=post, obj_in=obj_in)

    return post


@router.delete("/{post_id}", response_model=schemas.RemoveRowResult)
def delete_post(
    post_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(
        dependencies.get_current_active_user_in_admin_group
    ),
) -> schemas.RemoveRowResult:
    """게시물 삭제"""

    post = board_crud.get_active_one(db, _id=post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # author only.
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="게시글 작성자가 아닙니다."
        )

    # find replies and delete
    for re in post.replies:
        reply_crud.remove(db, re)

    # remove
    r = board_crud.remove(db, obj_in=post)

    return r


# @router.post(
#     "/{post_id}/activate",
#     response_model_exclude_none=True,
# )
# def activate_post(
#     post_id: int = Path(...),
#     db: Session = Depends(dependencies.get_session),
#     current_user: Union[models.User, models.Superuser] = Depends(
#         dependencies.get_admin_usergroup
#     ),
# ):
#     """게시물 활성화"""

#     post = board_crud.get(db, _id=post_id)

#     if current_user.id != post.author_id and not isinstance(
#         current_user, models.Superuser
#     ):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

#     post = board_crud.set_status(
#         db, _id=post_id, _status=schemas.Status.active
#     )

#     return post


# @router.delete(
#     "/{post_id}/deactivate",
#     response_model_exclude_none=True,
# )
# def deactivate_post(
#     post_id: int = Path(...),
#     db: Session = Depends(dependencies.get_session),
#     current_user: Union[models.User, models.Superuser] = Depends(
#         dependencies.get_admin_usergroup
#     ),
# ):
#     """게시물 비활성화"""
#     post = board_crud.get(db, _id=post_id)

#     if current_user.id != post.author_id and isinstance(
#         current_user, models.User
#     ):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

#     # set status
#     post = board_crud.set_status(
#         db, obj_in=post, _status=schemas.Status.inactive
#     )
#     return post


@router.post(
    "/{post_id}/replies",
    response_model_exclude_none=True,
)
def write_reply(
    obj_in: _ReplyCreate,
    post_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    """댓글 달기"""

    # get post
    post = board_crud.get_active_one(db, _id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시물을 찾을 수가 없습니다."
        )

    # write reply
    reply = reply_crud.create(
        db, obj_in=obj_in, post_id=post.id, writer_id=current_user.id
    )

    return reply


# 게시판을 불러올때 댓글리스트는 자동으로 불러와진다.
# @router.get(
#     "/{post_id}/replies",
#     response_model=List[_ReplyRead],
#     response_model_exclude_none=True,
# )
# def get_replies(
#     post_id: int = Path(...),
#     db: Session = Depends(dependencies.get_session),
# ) -> List[_ReplyRead]:
#     """댓글들 불러오기"""

#     # get post
#     post = board_crud.get_active_one(db, _id=post_id)

#     # return replies
#     return post.replies


@router.put(
    "/{post_id}/replies/{reply_id}",
    response_model=_ReplyRead,
    response_model_exclude_none=True,
)
def update_reply(
    obj_in: _ReplyUpdate,
    # post_id: int = Path(...),
    reply_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> _ReplyRead:
    """댓글 수정하기"""

    # get reply
    reply = reply_crud.get(db, _id=reply_id)
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="답글을 찾을 수 없습니다."
        )

    # only writer
    if reply.writer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="답글 작성자가 아닙니다."
        )

    # update
    reply = reply_crud.update(db, db_obj=reply, obj_in=obj_in)

    return reply


@router.delete(
    "/{post_id}/replies/{reply_id}", response_model=schemas.RemoveRowResult
)
def delete_reply(
    # post_id: int = Path(...),
    reply_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> schemas.RemoveRowResult:
    """댓글 (상태와 상관없이)삭제하기"""

    # get reply
    reply = reply_crud.get(db, _id=reply_id)
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="답글을 찾을 수 없습니다."
        )

    # writer only
    if reply.writer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="답글 작성자가 아닙니다."
        )

    # remove
    r = reply_crud.remove(db, obj_in=reply)

    return r
