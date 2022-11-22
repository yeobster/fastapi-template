import sys
from typing import Dict
from loguru import logger
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder

from main import app

import models, schemas, utils
from core.config import settings
from core import config
from tests import get_token_header, get_token, make_api_url, validate_response

client = TestClient(app)


def create_usergroup():
    pass


def change_usergroup():
    pass


def signup(obj_in):
    api = make_api_url("/auths/signup")
    jsonable = jsonable_encoder(obj_in)

    return client.post(api, json=jsonable)


def validate(user_in: Dict = None, auth_method: str = None):

    if auth_method is None:
        logger.critical(
            "인증방법을 선택하세요. \n1. 상단의 인증코드를 입력\n2.링크를 통해 인증(인증 후 선택하세요)"
        )
        auth_method = sys.stdin.readline()

    auth_method = auth_method.replace("\n", "")
    auth_method = auth_method.strip()

    if auth_method == "1":
        token: str = sys.stdin.readline()
        token = token.strip()
        query = "t=" + token
        api = make_api_url("/auths/user-authenticate?" + query)
        res = client.get(api)
        validate_response(res)

    elif auth_method == "2":
        token: schemas.Token = get_token(**user_in)
        return token


def get_me(t: schemas.Token):
    api = make_api_url("/users/me")
    return client.get(api, headers=get_token_header(t))


def update_me(t: schemas.Token, obj: models.UserUpdate):
    api = make_api_url("/users/me")
    jsonable = jsonable_encoder(obj)
    return client.put(api, headers=get_token_header(t), json=jsonable)


def test_user():

    # 유저 가입 후 로그인
    logger.info("게스트로 가입하기")
    guest_user1 = models.UserCreate(
        name=utils._random.get_korean_name(),
        email="blkpark@blkpark.com",
        nickname=utils._random.get_nickname(),
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/10695610?v=4",
        corp=utils._random.get_brand(),
        team=utils._random.get_team(),
        position=utils._random.get_position(),
        password=config.DEFAULT_PASSWORD,
        user_group_id=schemas.UserGroup.guest["id"],
        agree_terms=True,
        agree_private=True,
    )

    if settings.SENDGRID_CHECKING is False:
        # 인증 코드를 입력하지 않아도 되는 경우, 임시 이메일을 생성해서 로그인
        guest_user1.email = utils._random.get_email()

    res = signup(guest_user1)
    validate_response(res)

    if settings.AUTHENTICATION_CHECKING:
        logger.info("일반유저 가입시 이메일 인증 여부가 True이므로 인증을 해야 합니다.")
        logger.info("가입시 생성된 토큰를 통해 인증한다.")
        logger.debug("인증을 하지 않으면 로그인이 되지 않게 한다.")
        get_token(**guest_user1.dict(), compare_status_code=4)
        res = validate(guest_user1.dict())

    logger.info("로그인하기.")
    token: schemas.Token = get_token(**guest_user1.dict())

    logger.info("내 정보보기.")
    res = get_me(token)
    validate_response(res)
    guest_user1 = res.json()
    assert guest_user1["user_group_id"] == schemas.UserGroup.guest["id"]

    # 내 정보수정하기
    update_guest_user1 = models.UserUpdate(name="내 이름이 바뀜")
    res = update_me(t=token, obj=update_guest_user1)
    validate_response(res)

    res = get_me(t=token)
    validate_response(res)

    guest_user1 = res.json()
    assert guest_user1["name"] == update_guest_user1.name

    # 비밀번호 변경하기

    # logger.info("유저그룹 변경하기")
    # logger.debug("사용자는 유저그룹을 변경할 수 없다.")

    # should_fail_to_update_usergroup_data = {
    #     "user_group_id": schemas.UserGroup.admin["id"]
    # }

    # res = update_me(token, obj=should_fail_to_update_usergroup_data)
    # validate_response(res, response_code=4)

    # 관리자로 유저그룹 변경하기
    # logger.info("관리자 로그인")
    # usergroup_data_to_update = models.User(user_group=schemas.UserGroup.base)
