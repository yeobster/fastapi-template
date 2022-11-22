from typing import List
from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
import schemas, models, crud, core, utils

from router.backend import dependencies


router = APIRouter()


@router.post("", response_model=models.UserGroup)
def create_usergroup(
    usergroup_in: models.UserGroupCreate,
    db: Session = Depends(dependencies.get_session),
    _: models.User = Depends(dependencies.get_admin_usergroup),
):
    """
    유저그룹 생성
    """

    usergroup = crud.usergroup.get_by_name(db, usergroup_in.name)
    if usergroup:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 해당 그룹이 생성되어 있습니다.",
        )

    usergroup: models.UserGroup = crud.usergroup.create(
        db, obj_in=usergroup_in
    )

    return usergroup


@router.get("", response_model=List[models.UserGroup])
async def get_usergroup_list(
    db: Session = Depends(dependencies.get_session),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(dependencies.get_admin_usergroup),
) -> models.UserGroup:
    usergroups: List[models.UserGroup] = crud.usergroup.get_multi(
        db, skip=skip, limit=limit
    )

    return usergroups


@router.get("/{usergroup_id}")
def get_usergroup(
    db: Session = Depends(dependencies.get_session),
    usergroup_id: int = Path(..., alias="usergroup_id"),
    _: models.User = Depends(dependencies.get_admin_usergroup),
) -> models.UserGroup:
    usergroup: models.UserGroup = crud.usergroup.get(db, _id=usergroup_id)
    return usergroup


@router.put("/{usergroup_id}")
def update_usergroup(
    db: Session = Depends(dependencies.get_session),
    usergroup_id: int = Path(..., alias="usergroup_id"),
    usergroup_in: models.UserGroupUpdate = Body(...),
    _: models.User = Depends(dependencies.get_admin_usergroup),
) -> models.UserGroup:
    usergroup: models.UserGroup = crud.usergroup.get(db, _id=usergroup_id)
    if usergroup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

    usergroup: models.UserGroup = crud.usergroup.update(
        db=db, _id=usergroup_id, obj_in=usergroup_in, db_obj=usergroup
    )

    return usergroup


@router.delete("/{usergroup_id}")
def delete_usergroup(
    db: Session = Depends(dependencies.get_session),
    usergroup_id: int = Path(..., alias="usergroup_id"),
    _: models.User = Depends(dependencies.get_admin_usergroup),
) -> schemas.RemoveRowResult:

    base_usergroup_ids = schemas.usergroup.get_usergroup_id_list()
    if usergroup_id in base_usergroup_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="삭제할 수 없는 그룹입니다."
        )

    usergroup: models.UserGroup = crud.usergroup.get(db, _id=usergroup_id)
    if usergroup is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

    r = crud.usergroup.remove(db, _id=usergroup_id)

    return r
