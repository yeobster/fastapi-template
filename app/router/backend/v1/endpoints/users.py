from typing import List

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

import crud, models
from router.backend import dependencies

router = APIRouter()


@router.get(
    "",
    response_model=List[models.UserPublicRead],
)
def read_users(
    _: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_session),
    skip: int = 0,
    limit: int = 100,
) -> models.User:
    """
    일반 유저 리스트를 가지고 온다.
    """
    users: List[models.User] = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get(
    "/me",
    response_model=models.UserPrivateRead,
)
def get_me(
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.User:
    """
    현재 본인의 정보를 가지고 올 수 있다.
    """

    return current_user


@router.put(
    "/me",
    response_model=models.User,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def update_me(
    *,
    user_in: models.UserUpdate,
    db: Session = Depends(dependencies.get_session),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> models.User:
    """
    내 정보 수정
    """

    # update
    user: models.User = crud.user.update(
        db, db_obj=current_user, obj_in=user_in
    )

    return user


@router.get("/{user_id}", response_model=models.UserPublicRead)
def get_user_by_id(
    _: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_session),
    user_id: int = Path(...),
) -> models.UserPublicRead:
    """
    유저정보보기 - 일반유저가 다른 일반유저를 조회할때
    """

    user: models.User = crud.user.get(db, _id=user_id)

    return user


@router.post("/{user_id}/activate", response_model=models.User)
def activate_user(
    _: models.User = Depends(dependencies.get_admin_usergroup),
    db: Session = Depends(dependencies.get_session),
    user_id: int = Path(...),
) -> models.User:
    """
    유저 활성화
    """

    user: models.User = crud.user.activate(db, _id=user_id)
    return user


@router.post("/{user_id}/deactivate", response_model=models.User)
def deactivate_user(
    _: models.User = Depends(dependencies.get_admin_usergroup),
    db: Session = Depends(dependencies.get_session),
    user_id: int = Path(...),
) -> models.User:
    """
    유저 활성화
    """

    user: models.User = crud.user.deactivate(db, _id=user_id)
    return user
