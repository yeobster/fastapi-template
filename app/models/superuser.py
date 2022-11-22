# third party
from sqlmodel import Field

# user defined
from models.base import ModelBase
from models.mixin import (
    AccountMixIn,
    AccountPrivateMixIn,
    AuthorizationMixIn,
    DatetimeMixIn,
)


### models ###


class SuperuserBase(AccountMixIn):
    pass


class SuperuserCreate(SuperuserBase, AccountPrivateMixIn):
    """생성 객체"""

    pass


class SuperuserUpdate(SuperuserBase):
    """업데이트 객첵"""

    pass


class SuperuserPublicRead(SuperuserBase, DatetimeMixIn):
    """공개 정보"""

    id: int


class SuperuserPrivateRead(
    SuperuserPublicRead, AccountPrivateMixIn, AuthorizationMixIn
):
    """
    관리자 개인정보
    """

    created_user_id: int = Field(title="계정을 생성한 관리자계정")


# 주의: 마지막 파라메터부터 컬럼이 생성됨
class Superuser(
    DatetimeMixIn,
    AuthorizationMixIn,
    AccountPrivateMixIn,
    SuperuserBase,
    ModelBase,
    table=True,
):
    """
    관리자 계정
    """

    pass
