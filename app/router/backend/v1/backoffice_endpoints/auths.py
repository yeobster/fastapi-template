# TODO: 아래 기능은 검증되지 않음. 구현해야함.

# std
from datetime import timedelta
from typing import Union, Any
from loguru import logger

# third party
from sqlalchemy.orm import Session

# fastapi
from fastapi import APIRouter, Depends, status, Query, Path, Body
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from router.backend import dependencies

# user defined
from core.config import settings
import core, schemas, crud, models


router = APIRouter()


@router.post(
    "/signup",
    response_model=models.SuperuserPrivateRead,
)
def create_user(
    user_in: models.SuperuserCreate = Depends(
        dependencies.validate_signup_backoffice
    ),
    db: Session = Depends(dependencies.get_session),
) -> models.SuperuserPrivateRead:
    """
    일반유저 가입
    """

    # DB insert
    user: models.Superuser = crud.user.signup(db, obj_in=user_in)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="유저를 생성하지 못했습니다."
        )

    # 계정 이메일 인증허용시 유저인증용 토큰 생성하고 이메일을 전송한다.
    if settings.BACKOFFICE_AUTHENTICATION_CHECKING:
        token_sub = schemas.TokenPayloadSub(
            id=user.id,
            scope=schemas.Scope.superuser,
            token_type=schemas.TokenType.user_authentication,
        )

        token = core.security.create_authentication_token(token_sub=token_sub)
        auth_link = core._func.make_auth_link(token)

        # print auth_link
        logger.critical(f"\n[유저 {user.email}]\n토큰: {token}\n인증링크: {auth_link}")

        # TODO: 메일 전송

    return user


@router.get("/user-authenticate")
def user_authenticate(
    db: Session = Depends(dependencies.get_session), t: str = Query(...)
):
    core.security.verify_token_payload_sub(token=t, is_superuser=True)
    payload_sub: schemas.TokenPayloadSub = core.security.decode_token(token=t)
    superuser = crud.superuser.activate(db, _id=payload_sub.id)
    superuser = crud.superuser.authorize(db, db_obj=superuser)

    return superuser


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: Session = Depends(dependencies.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> schemas.Token:
    """
    subject에 유저타입을 넣어서 parsing 가능하게 구현하고, token 발급은 API하나만 사용한다.
    """

    obj = {"email": form_data.username, "password": form_data.password}
    superuser: models.Superuser = crud.superuser.authenticate(db, **obj)

    # 계정이 없으면 에러
    if superuser is None:
        raise HTTPException(
            status_code=401,
            detail="계정인증에 실패하였습니다. 활성화되지 않은 계정 이거나 로그인 정보가 틀렸습니다.",
        )

    payload_sub = schemas.TokenPayloadSub(
        id=superuser.id,
        scope=schemas.Scope.superuser,
        token_type=schemas.TokenType.login,
    )

    # status가 active 아니면 에러
    if superuser.status != schemas.Status.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="계정인증에 실패하였습니다. 활성화되지 않은 계정 이거나 로그인 정보가 틀렸습니다.",
        )

    token: schemas.Token = core.security.create_token(payload_sub=payload_sub)

    return token


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(
    email: str = Depends(dependencies.find_email_in_all_accounts),
    db: Session = Depends(dependencies.get_session),
) -> Any:
    """
    비밀번호 재설정, 리턴되는 type은 크게 신경쓸 필요 없음. 토큰에 정보가 들어가 있음.
    """

    # 이메일 체크
    account: Any = None
    subject: str = ""

    while True:
        account: models.Superuser = crud.superuser.get_by_email(
            db, email=email
        )
        if account:
            account_type = "admin"
            subject = str(account.id) + "," + account_type
            break

        user: models.User = crud.user.get_by_email(db, email=email)
        if user:
            account_type = "user"
            subject = str(user.id) + "," + account_type
            break

        break

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저 이메일이 존재하지 않습니다.",
        )

    # 비밀번호 변경하기 토큰 발행
    password_reset_token = core.security.generate_password_reset_token(
        subject=subject
    )

    is_sended = core._mailer._password.send_recovery(
        email=email,
        token=password_reset_token,
        target_url="",
        account_type=account_type,
    )

    if is_sended is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메일 전송에 실패하였습니다.",
        )

    return {"msg": "복구 메일이 전송되었습니다."}


@router.post("/reset-password", response_model=schemas.Msg)
def reset_password(
    password_in: str = Body(...),
    db: Session = Depends(dependencies.get_session),
    current_user: Any = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    비밀번호 리셋 (비밀번호 재설정)
    """

    # 해쉬 생성
    hashed_password = core.security.get_password_hash(password_in)
    current_user.password = hashed_password

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"msg": "비밀번호가 성공적으로 변경되었습니다."}


# @router.post("/password-temporary/{email}", response_model=schemas.Msg)
# def temp_password(
#     email: str = Path(...), db: Session = Depends(dependencies.get_session)
# ) -> Any:

#     # 이메일 체크

#     while True:
#         user = crud.superuser.update_password_by_email(db, email=email)
#         if user is not None:
#             break

#         user = crud.user.update_password_by_email(db, email=email)
#         if user is not None:
#             break

#         break

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="유저 이메일이 존재하지 않습니다.",
#         )

#     return {"msg": "임시 비밀번호 메일이 전송되었습니다."}
