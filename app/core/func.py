from core.config import settings


def make_auth_link(token: str, is_superuser: bool = False) -> str:
    """
    이메일 인증 링크를 만드는 함수
    """

    base_api = "/api/v1"
    request_auth_api = "/auths/user-authenticate"  # user router

    # superuser router
    if is_superuser:
        request_auth_api = "/backoffice" + request_auth_api

    # set api path
    request_auth_api = base_api + request_auth_api

    # make auth link
    auth_link = (
        "http://"
        + settings.AUTHENTICATION_HOST
        + ":"
        + settings.AUTHENTICATION_PORT
        + request_auth_api
        + "?t="
        + token
    )
    return auth_link
