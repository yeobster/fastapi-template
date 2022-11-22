from typing import Optional, Literal
from pydantic import BaseModel


class TokenSubParseError(Exception):
    """
    커스텀한 토큰을 파싱할 때 생성되는 에러
    """

    def __init__(self) -> None:
        super().__init__("토큰을 파싱할 수 없습니다.")


class Token(BaseModel):
    """
    HTTP 응답으로 사용되는 토큰 클래스
    """

    access_token: str
    token_type: str = "bearer"


class Scope:
    """
    계정별로 토큰을 구분하는 클래스
    """

    user = "user_type"
    superuser = "superuser_type"


class TokenType:
    login: str = "login"
    user_authentication: str = "user_authentication"
    reset_password: str = "reset_password"


class TokenPayloadSub(BaseModel):
    """
    실제 토큰에 담겨져 있는 정보
    """

    id: int
    scope: Literal[Scope.user, Scope.superuser]
    token_type: Literal[
        TokenType.login,
        TokenType.user_authentication,
        TokenType.reset_password,
    ]

    def get_subject(self):
        subject = f"{self.id},{self.scope},{self.token_type}"
        return subject


class TokenPayload(BaseModel):
    """_
    디코드된 jwt 객체
    """

    sub: Optional[str] = None

    def parse(self) -> TokenPayloadSub:
        splited = self.sub.split(",")

        if len(splited) != 3:
            raise TokenSubParseError()

        return TokenPayloadSub(
            id=splited[0], scope=splited[1], token_type=splited[2]
        )
