from typing import Union
from loguru import logger
import schemas, core
from core.config import settings
import models


def send_auth_link(obj_in: Union[models.Superuser, models.User]) -> bool:
    scope = schemas.Scope.user
    if isinstance(obj_in, models.Superuser):
        scope = schemas.Scope.superuser

    token_sub = schemas.TokenPayloadSub(
        id=obj_in.id,
        scope=scope,
        token_type=schemas.TokenType.user_authentication,
    )
    token = core.security.create_authentication_token(token_sub=token_sub)
    auth_link = core._func.make_auth_link(token)

    # print auth_link
    logger.critical(f"\n[유저 {obj_in.email}]\n토큰: {token}\n인증링크: {auth_link}")

    # send mail (active로 생성될 때만 메일 전송)
    if settings.SENDGRID_API_KEY is not None:

        subject = f"[{settings.PROJECT_NAME}] 인증메일"
        body_title = "계정인증"
        body = f"{obj_in.email}  / {obj_in.nickname} <br> 가입정보를 인증하려면 아래의 링크를 클릭하세요."

        dt = schemas.DynamicTemplate(
            subject=subject,
            body_title=body_title,
            body=body,
            contents=auth_link,
        )
        de = schemas.DynamicEmail(
            to_email=obj_in.email,
            template=dt,
            template_id=settings.SENDGRID_AUTH_TEMPLATE,
        )

        res = de.send_email()
        if res.status_code / 100 == 2:
            logger.critical(f"메일 전송에 실패하였습니다. {de}")
            return False

        return True


def send_congratulations_for_user(obj_in: models.User) -> bool:
    account_type: str = "사용자"
    return send_congratulations(obj_in, account_type)


def send_congratulations_for_superuser(obj_in: models.Superuser) -> bool:
    account_type = "관리자"
    return send_congratulations(obj_in.email, account_type)


def send_congratulations(
    obj_in: Union[models.Superuser, models.User], account_type: str
) -> bool:

    # send mail (active로 생성될 때만 메일 전송)
    if settings.SENDGRID_API_KEY is not None:

        subject = f"[{settings.PROJECT_NAME}] {account_type}로 추가되었습니다."
        body_title = f"{account_type} 계정생성"
        body = f"{obj_in.email}  / {obj_in.nickname} 계정 발급이 되었습니다."

        dt = schemas.DynamicTemplate(
            subject=subject,
            body_title=body_title,
            body=body,
        )
        de = schemas.DynamicEmail(
            to_email=obj_in.email,
            template=dt,
            template_id=settings.SENDGRID_BASE_TEMPLATE,
        )

        res = de.send_email()
        if res.status_code / 100 == 2:
            logger.critical(f"메일 전송에 실패하였습니다. {de}")
            return False

        return True
