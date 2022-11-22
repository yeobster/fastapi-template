# TODO: 아래 기능은 검증되지 않음. 구현해야함.
from typing import List
from sqlmodel import Session
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Path,
)

# core
import crud, models

# import crud, models, mailer, schemas
from router.backend import dependencies

router = APIRouter()


@router.post(
    "",
    response_model=models.Superuser,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def create_superuser(
    superuser_in: models.SuperuserCreate,
    db: Session = Depends(dependencies.get_session),
    current_user: models.Superuser = Depends(dependencies.validate_signup),
) -> models.Superuser:
    """
    관리자 계정 생성
    """

    # 생성한 계정정보 추가
    # db insert
    superuser = crud.superuser.signup(
        db, obj_in=superuser_in, current_user=current_user
    )

    if not superuser:
        raise HTTPException(400, detail="유저를 생성하지 못했습니다.")

    # TODO: 메일전송 구현
    # # 비활성화 상태로 생성된 계정을 제외하고 메일을 전송한다.
    # if superuser.status is not schemas.Status.inactive:
    #     mailer.signup.send_signup_mail(obj_in=superuser)

    return superuser


@router.get(
    "",
    response_model=List[models.Superuser],
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def get_list_superusers(
    db: Session = Depends(dependencies.get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
) -> List[models.Superuser]:
    """
    get superuser list.
    """

    superusers = crud.superuser.get_multi(db, skip=skip, limit=limit)
    return superusers


@router.get(
    "/me",
    response_model=models.Superuser,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def get_me(
    current_user: models.Superuser = Depends(
        dependencies.get_current_superuser
    ),
) -> models.Superuser:
    """
    superuser계정 본인의 정보를 가지고 온다.
    """
    return current_user


@router.patch(
    "/me",
    response_model=models.Superuser,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def patch_me(
    superuser_in: models.SuperuserUpdate,
    db: Session = Depends(dependencies.get_session),
    current_user: models.Superuser = Depends(
        dependencies.get_current_active_superuser
    ),
) -> models.Superuser:
    """
    superuser계정 본인의 정보를 가지고 온다.
    """

    # update
    superuser = crud.superuser.update(
        db, db_obj=current_user, obj_in=superuser_in
    )

    return superuser


@router.get(
    "/{superuser_id}",
    response_model=models.Superuser,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def get_superuser(
    db: Session = Depends(dependencies.get_current_active_superuser),
    superuser_id: int = Path(...),
) -> models.Superuser:
    """
    superuser 정보를 가지고 온다
    """
    superuser = crud.superuser.get(db, _id=superuser_id)
    if superuser is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"비활성화된 superuser({superuser_id})입니다.",
        )
    return superuser


@router.patch(
    "/{superuser_id}",
    response_model=models.Superuser,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def update_superuser(
    superuser_in: models.SuperuserUpdate,
    superuser_id: int = Path(...),
    db: Session = Depends(dependencies.get_session),
    _: models.Superuser = Depends(dependencies.get_current_active_superuser),
) -> models.Superuser:
    """
    superuser 정보를 수정한다.
    """
    # superuser 정보 확인
    superuser = crud.superuser.get(db, id=superuser_id)
    if superuser is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="유저를 찾을 수 없습니다.")

    # update
    superuser = crud.superuser.update(
        db, db_obj=superuser, obj_in=superuser_in, is_set_updated_at=True
    )

    return superuser


@router.delete("/{superuser_id}")
def delete_superuser(
    db: Session = Depends(dependencies.get_session),
    _: models.Superuser = Depends(dependencies.get_current_active_superuser),
    superuser_id: int = Path(...),
):
    """
    관리자를 삭제한다.
    """
    if superuser_id == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="초기관리자계정은 삭제 또는 수정 할 수 없습니다.",
        )

    superuser = crud.superuser.get(db, _id=superuser_id)
    if superuser is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"삭제할 관리자({superuser_id})를 찾을 수 없습니다."
        )

    return crud.superuser.remove(db, _id=superuser_id)


@router.post("/{superuser_id}/activate")
def activate_superuser(
    db: Session = Depends(dependencies.get_session),
    _: models.Superuser = Depends(dependencies.get_current_active_superuser),
    superuser_id: str = Path(...),
) -> models.Superuser:
    """
    superuser 활성화
    """
    if superuser_id == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="초기관리자계정은 삭제 또는 수정 할 수 없습니다.",
        )

    superuser = crud.superuser.activate(db, _id=superuser_id)

    # TODO: send mail 구현
    # if superuser.is_authorized == False:
    #     send_status = mailer.signup.send_signup(obj_in=superuser)
    #     if send_status is True:
    #         # db에 상태를 업데이트 한다.
    #         superuser: models.Superuser = crud.superuser.set_is_send_signup(
    #             db, model=superuser
    #         )

    return superuser


@router.delete("/{superuser_id}/deactivate")
def deactivate_superuser(
    db: Session = Depends(dependencies.get_session),
    _: models.Superuser = Depends(dependencies.get_current_active_superuser),
    superuser_id: int = Path(...),
) -> models.Superuser:
    """
    superuser 비활성화
    """

    if superuser_id == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="초기관리자계정은 삭제 또는 수정 할 수 없습니다.",
        )

    superuser = crud.superuser.deactivate(db, _id=superuser_id)

    return superuser
