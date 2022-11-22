from loguru import logger
from fastapi.testclient import TestClient
from fastapi.responses import Response
from schemas.token import Token


from main import app

CLIENT = TestClient(app)


def make_api_url(api_path: str, base_url="/api/v1"):
    if not api_path.startswith("/"):
        raise Exception("api_path는 /로 시작되야 합니다.")
    return base_url + api_path


def get_token_header(token: Token):
    """
    헤더에 사용할 토큰 dict를 return
    """

    return {"Authorization": token.token_type + " " + token.access_token}


def get_token(is_superuser: bool = False, **kwargs) -> Token:
    """
    토큰 얻기
    """
    base_url = "/api/v1"

    # change base_url
    if is_superuser:
        base_url += "/backoffice"

    api = base_url + "/auths/login/access-token"
    compare_status_code = 2

    if "compare_status_code" in kwargs:
        compare_status_code = kwargs["compare_status_code"]

    logger.trace(f"get token response가 {compare_status_code}xx가 맞는지 비교합니다.")

    get_token_user = {
        "username": kwargs["email"],
        "password": kwargs["password"],
    }
    res = CLIENT.post(api, data=get_token_user)
    status_code_x = int(res.status_code / 100)
    assert status_code_x == compare_status_code

    if status_code_x == 2:
        t: Token = Token(**res.json())
        # type check
        assert t.token_type == "bearer"
        return t
    else:
        return


def validate_response(response: Response, response_code: int = 2):
    """
    assert: response가 2xx
    """
    status = int(response.status_code / 100)

    assert status == response_code
