from typing import Any
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import schemas
import models
from main import app
from tests import get_token_header, make_api_url

client = TestClient(app)


def get_post(board_name: str, post_id: int, t: schemas.Token):
    api_path = "/boards/" + board_name + "/" + str(post_id)
    api = make_api_url(api_path=api_path)
    return client.get(api, headers=get_token_header(t))


def get_post_list(
    board_name: str,
    t: schemas.Token,
    skip: int = 0,
    limit: int = 10,
):
    api_path = "/boards/" + board_name
    api = make_api_url(api_path=api_path)
    params = {"skip": skip, "limit": limit}
    return client.get(api, headers=get_token_header(t), params=params)


def write_post(board_name: str, obj_in: Any, t: schemas.Token):
    api_path = "/boards/" + board_name
    api = make_api_url(api_path=api_path)
    print(api)
    jsonable = jsonable_encoder(obj_in)
    return client.post(api, json=jsonable, headers=get_token_header(t))


def update_post(board_name: str, post_id: int, obj_in: Any, t: schemas.Token):
    api_path = "/boards/" + board_name + "/" + str(post_id)
    api = make_api_url(api_path=api_path)
    jsonable = jsonable_encoder(obj_in)
    return client.put(api, json=jsonable, headers=get_token_header(t))


def delete_post(board_name: str, post_id: int, t: schemas.Token):
    api_path = "/boards/" + board_name + "/" + str(post_id)
    api = make_api_url(api_path=api_path)
    return client.delete(api, headers=get_token_header(t))


def activate_post():
    pass


def deactivate_post():
    pass


### replies ###
def write_reply(board_name: str, post_id: int, obj_in: Any, t: schemas.Token):
    api_path = "/boards/" + board_name + "/" + str(post_id) + "/replies"
    api = make_api_url(api_path=api_path)
    jsonable = jsonable_encoder(obj_in)
    return client.post(api, json=jsonable, headers=get_token_header(t))


def update_reply(
    board_name: str, post_id: int, reply_id: int, obj_in: Any, t: schemas.Token
):
    api_path = (
        "/boards/"
        + board_name
        + "/"
        + str(post_id)
        + "/replies/"
        + str(reply_id)
    )
    api = make_api_url(api_path=api_path)
    jsonable = jsonable_encoder(obj_in)

    return client.put(api, json=jsonable, headers=get_token_header(t))


def delete_reply(
    board_name: str, post_id: int, reply_id: int, t: schemas.Token
):
    api_path = (
        "/boards/"
        + board_name
        + "/"
        + str(post_id)
        + "/replies/"
        + str(reply_id)
    )
    api = make_api_url(api_path=api_path)
    print(api)
    return client.delete(api, headers=get_token_header(t))
