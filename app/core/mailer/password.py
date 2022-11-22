from fastapi import HTTPException, status
from pydantic import EmailStr
from loguru import logger
from core.config import settings
import core
import schemas


def send_temp(email: str, temp_pass: str, type_string: str):
    """
    임시 비밀번호를 이메일로 전송한다.
    """
    t = {
        "subject": "[" + settings.PROJECT_NAME + "] 인증코드",
        "body_title": "임시 비밀번호 발송안내",
        "body": "아래의 임시 비밀번호를 사용하여 로ㄴ그인 하세요",
        "contents": "계정 유형 : " + type_string + ", 임시 비밀번호 : " + temp_pass,
    }
    dt = schemas.DynamicTemplate(**t)

    # make dynamic mail
    de = schemas.DynamicEmail(
        to_email=email, template=dt, template_id=schemas.TemplateEnum.auth
    )

    # send mail
    res = de.send_email()
    if res.status_code / 100 == 2:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="메일 전송에 실패하였습니다."
        )

    return res


def send_reset(_id: str, email: EmailStr) -> bool:
    """
    이메일을 이용하여 리셋 URL을 전송한다.
    """

    password_reset_token = core.security.generate_password_reset_token(
        subject=str(_id) + "," + "user"
    )
    subject = f"[{settings.PROJECT_NAME}] 비밀번호 초기화"

    body_title = "비밀번호 초기화"
    body = email + " 비밀번호 초기화를 요청하였습니다. 비밀번호 초기화를 위해 다음 링크를 클릭해 주세요"

    contents = settings.PASSWORD_RESET_URL + "?token=" + password_reset_token

    dt = schemas.DynamicTemplate(
        subject=subject,
        body_title=body_title,
        body=body,
        contents=contents,
    )
    de = schemas.DynamicEmail(
        to_email=email,
        template=dt,
        template_id=schemas.TemplateEnum.auth,
    )
    res = de.send_email()
    if res.status_code / 100 == 2:
        logger.critical(f"메일 전송에 실패하였습니다. {de}")
        return False

    return True


def send_recovery(
    email, password_reset_token, target_url, account_type
) -> bool:
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
    de = schemas.DynamicEmail(
        to_email=email, template=dt, template_id=schemas.TemplateEnum.auth
    )

    # send mail
    res = de.send_email()
    if res.status_code / 100 == 2:
        return False

    return True
