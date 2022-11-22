# std
from typing import Any
from loguru import logger

# third party
from sqlmodel import Session

# fastapi
from fastapi import APIRouter, Depends, status, Query
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from router.backend import dependencies

# user defined
from core.config import settings
from core import _mailer
import core, schemas, crud, models


router = APIRouter()


@router.post(
    "/signup",
    response_model=models.UserPrivateRead,
)
def create_user(
    user_in: models.UserCreate = Depends(dependencies.validate_signup_base),
    db: Session = Depends(dependencies.get_session),
) -> models.User:
    """
    일반유저 가입
    """

    # DB insert
    user: models.User = crud.user.signup(db, obj_in=user_in)

    if not user:
        raise HTTPException(400, detail="유저를 생성하지 못했습니다.")

    # 계정 이메일 인증허용시 유저인증용 토큰 생성하고 이메일을 전송한다.
    if settings.AUTHENTICATION_CHECKING:

        if not _mailer.signup.send_auth_link(obj_in=user):
            logger.critical("인증메일을 전송하지 못했습니다.")

    else:

        # status를 활성화한다.
        user = crud.user.activate(db, _id=user.id)

        # 유저인증이 필요없다면 바로 가입환영메일을 보내고 자동으로 이메일 승인시킨다.
        user = crud.user.authorize(db, db_obj=user)

        # 가입환영 메일을 보낸다.
        if settings.SENDGRID_CHECKING:
            if not _mailer.signup.send_congratulations_for_user(obj_in=user):
                logger.critical("가입 메일을 전송하지 못했습니다.")

    return user


@router.get("/user-authenticate")
def user_authenticate(
    db: Session = Depends(dependencies.get_session), t: str = Query(...)
):
    # 토큰이 올바른지 확인한다.
    payload_sub: schemas.TokenPayloadSub = core.security.decode_token(token=t)
    if payload_sub.token_type is not schemas.TokenType.user_authentication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="토큰타입이 올바르지 않습니다."
        )

    # 토큰 스코프가 user인지 확인한다.
    if payload_sub.scope is not schemas.Scope.user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 스코프가 맞지 않습니다.",
        )

    # status를 활성화한다.
    user = crud.user.activate(db, _id=payload_sub.id)

    # 유저의 이메일 승인 여부를 설정한다.
    user = crud.user.authorize(db, db_obj=user)

    # 가입환영 메일을 보낸다.
    if settings.SENDGRID_CHECKING:
        _mailer.signup.send_congratulations_for_user(obj_in=user)

    return user


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: Session = Depends(dependencies.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> schemas.Token:
    """
    subject에 유저타입을 넣어서 parsing 가능하게 구현하고, token 발급은 API하나만 사용한다.
    """

    obj = {"email": form_data.username, "password": form_data.password}
    user: models.User = crud.user.authenticate(db, **obj)

    # 계정이 없으면 에러
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="계정인증에 실패하였습니다. 활성화되지 않은 계정 이거나 로그인 정보가 틀렸습니다.",
        )

    payload_sub = schemas.TokenPayloadSub(
        id=user.id,
        scope=schemas.Scope.user,
        token_type=schemas.TokenType.login,
    )

    # if user status가 존재한다면
    if user.status != schemas.Status.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="계정인증에 실패하였습니다. 활성화되지 않은 계정 이거나 로그인 정보가 틀렸습니다.",
        )

    token: schemas.Token = core.security.create_token(payload_sub=payload_sub)

    # # 만료시간 세팅
    # access_token_expires = timedelta(
    #     minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    # )

    # # create token
    # access_token = core.security.create_access_token(
    #     subject=payload_sub.get_subject(), expires_delta=access_token_expires
    # )

    # token = schemas.Token(access_token=access_token)

    return token


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(
    email: str,
    target_url: str,
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

    # make template
    t = {
        "subject": "[" + settings.PROJECT_NAME + "] 인증코드",
        "body_title": "비밀번호 리셋 인증코드",
        "body": "아래 링크를 클릭하여 비밀번호를 재설정하세요",
        "contents": target_url
        + "?token="
        + password_reset_token
        + "&type="
        + account_type
        + "&email="
        + email,
    }
    dt = schemas.DynamicTemplate(**t)

    # make dynamic mail
    e = schemas.DynamicEmail(
        to_email=email, template=dt, template_id=schemas.TemplateEnum.auth
    )

    # send mail
    res = e.send_email()
    if res.status_code / 100 == 2:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="메일 전송에 실패하였습니다."
        )

    return {"msg": "복구 메일이 전송되었습니다."}


# @router.post("/reset-password", response_model=schemas.Msg)
# def reset_password(
#     password_in: schemas.ResetPasswordRequest,
#     db: Session = Depends(dependencies.get_session),
#     current_user: Any = Depends(dependencies.get_current_any_user),
# ) -> Any:
#     """
#     비밀번호 리셋 (일반유저, 슈퍼유저)
#     """

#     # 해쉬 생성
#     hashed_password = core.security.get_password_hash(password_in.new_password)
#     current_user.password = hashed_password

#     db.add(current_user)
#     db.commit()
#     db.refresh(current_user)
#     return {"msg": "비밀번호가 성공적으로 변경되었습니다."}


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
