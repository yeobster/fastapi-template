from loguru import logger
from lorem_text import lorem


from tests import get_token, validate_response


from core.config import settings
from core import config

import utils
from models import boards as board_models
from tests.board_base import (
    get_post,
    get_post_list,
    write_post,
    update_post,
    delete_post,
    activate_post,
    deactivate_post,
    write_reply,
    delete_reply,
    update_reply,
)


def test_board():

    logger.info("로그인하기")

    # FIXME: superuser를 구현하고 다시 개발
    # superuser = get_token(
    #     is_superuser=True,
    #     email="blake@blkpark.com",
    #     password=config.DEFAULT_PASSWORD,
    #     is_user=False,
    # )
    admin_user = get_token(
        email="blake@blkpark.com", password=config.DEFAULT_PASSWORD
    )
    admin_user2 = get_token(
        email="jiwon@blkpark.com", password=config.DEFAULT_PASSWORD
    )
    base_user = get_token(
        email="beomhwan@blkpark.com", password=config.DEFAULT_PASSWORD
    )
    base_user2 = get_token(
        email="jihoon@blkpark.com", password=config.DEFAULT_PASSWORD
    )
    guest_user = get_token(
        email="jcargun@blkpark.com", password=config.DEFAULT_PASSWORD
    )
    guest_user2 = get_token(
        email="jslee@blkpark.com",
        password=config.DEFAULT_PASSWORD,
    )

    logger.info("START notice 게시판 TEST......")

    # FIXME: superuser를 구현하고 다시 개발
    # logger.info("superuser가 게시합니다. 하지만 실패해야합니다.")
    # res = write_post("notice", obj_in=get_notice_create(), t=superuser)
    # validate_response(res, response_code=4)

    logger.info("base_user가 게시합니다. 하지만 실패해야합니다.")
    res = write_post("notice", obj_in=get_notice_create(), t=base_user)
    validate_response(res, response_code=4)

    logger.info("guest_user가 게시합니다. 하지만 실패해야합니다.")
    res = write_post("notice", obj_in=get_notice_create(), t=guest_user)
    validate_response(res, response_code=4)

    logger.info("admin_user2가 게시합니다.")
    res = write_post("notice", obj_in=get_notice_create(), t=admin_user2)
    validate_response(res)
    notice_1 = res.json()
    logger.info(notice_1)

    logger.info("admin_user가 게시합니다.")
    res = write_post("notice", obj_in=get_notice_create(), t=admin_user)
    validate_response(res)
    notice_2 = res.json()
    logger.info(notice_2)

    res = get_post_list("notice", t=admin_user, skip=0, limit=10)
    validate_response(res)
    jsonable = res.json()
    total_count = jsonable["all_post_count"]

    logger.info("admin_user가 작성한 notice_2의 게시물의 제목과 내용을 변경합니다.")
    logger.info("작성자만 변경할 수 있습니다.")
    logger.info("작성자가 아닌사람이 변경을 시도합니다.")
    res = update_post(
        "notice", notice_2["id"], obj_in=get_notice_update(), t=admin_user2
    )
    validate_response(res, response_code=4)

    logger.info("작성자가 변경을 시도합니다.")
    res = update_post(
        "notice", notice_2["id"], obj_in=get_notice_update(), t=admin_user
    )
    validate_response(res)

    logger.info("admin_user가 게시한 게시글에 댓글을 작성합니다.")
    write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=guest_user,
    )
    write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=admin_user,
    )
    write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=admin_user2,
    )
    write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=base_user,
    )
    write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=admin_user,
    )

    logger.info("notice_2에 guest_user2가 작성한 댓글을 변경합니다. 작성자만 변경이 가능합니다.")
    logger.info("notice_2에 guest_user2가 작성한 댓글을 admin_user가 변경을 시도합니다..")
    res = write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=guest_user2,
    )
    validate_response(res)
    notice_2_reply_guest_user2 = res.json()

    res = update_reply(
        "notice",
        post_id=notice_2["id"],
        reply_id=notice_2_reply_guest_user2["id"],
        obj_in=get_notice_reply_update(),
        t=admin_user,
    )
    validate_response(res, response_code=4)

    res = update_reply(
        "notice",
        post_id=notice_2["id"],
        reply_id=notice_2_reply_guest_user2["id"],
        obj_in=get_notice_reply_update(),
        t=guest_user2,
    )
    validate_response(res)

    logger.info("notice_2에 base_user2가 답급을 작성합니다.")
    res = write_reply(
        "notice",
        post_id=notice_2["id"],
        obj_in=get_notice_reply_create(),
        t=base_user2,
    )

    validate_response(res)
    notice_2_reply_base_user_2 = res.json()

    logger.info(
        "notice_2에 base_user2가 작성한 댓글을 admin_user가 삭제를 시도합니다..작성자만 삭제가능합니다."
    )
    res = delete_reply(
        "notice",
        post_id=notice_2["id"],
        reply_id=notice_2_reply_base_user_2["id"],
        t=admin_user,
    )
    validate_response(res, response_code=4)

    logger.info("notice_2에 base_user2가 작성한 댓글을 base_user2가 삭제를 시도합니다..")
    res = delete_reply(
        "notice",
        post_id=notice_2["id"],
        reply_id=notice_2_reply_base_user_2["id"],
        t=base_user2,
    )
    validate_response(res)

    res = get_post_list("notice", t=admin_user, skip=0, limit=10)
    validate_response(res)
    jsonable = res.json()
    assert jsonable["all_post_count"] == total_count
    logger.info(jsonable)

    logger.info("admin_user2가 게시한 notice_1를 admin_user가 삭제를 시도합니다.")
    logger.info("작성자만 삭제가능합니다.")
    res = delete_post("notice", post_id=notice_1["id"], t=admin_user)
    validate_response(res, response_code=4)

    logger.info("admin_user2가 게시한 notice_1를 삭제합니다. 댓글도 모두 사라집니다.")
    res = delete_post("notice", post_id=notice_1["id"], t=admin_user2)
    validate_response(res)
    total_count = total_count - 1

    res = get_post_list("notice", t=admin_user, skip=0, limit=10)
    validate_response(res)
    jsonable = res.json()
    assert jsonable["all_post_count"] == total_count

    logger.info("admin_user가 게시한 notice_2를 삭제합니다. 댓글도 모두 사라집니다.")
    res = delete_post("notice", post_id=notice_2["id"], t=admin_user)
    validate_response(res)
    total_count = total_count - 1

    res = get_post_list("notice", t=admin_user, skip=0, limit=10)
    validate_response(res)
    jsonable = res.json()
    assert jsonable["all_post_count"] == total_count


def get_notice_reply_create():
    return board_models.BoardNoticeReplyCreate(
        contents=lorem.words(utils._random.get_int(3, 8)),
    )


def get_notice_reply_update():
    return board_models.BoardNoticeReplyUpdate(contents="우크라이나가 한국무기 산다네요")


def get_notice_update():
    _body = "불러 인간이 천고에 인간의 못할 봄바람이다. 품으며, 보이는 부패를 간에 능히 소금이라 가장 어디 이상이 교향악이다. 그들의 영원히 그들을 남는 사막이다. 용기가 그들의 옷을 커다란 생생하며, 생의 것이다. 낙원을 돋고, 보이는 청춘의 힘차게 있으랴? 천자만홍이 따뜻한 현저하게 이상을 피부가 것이다. 그들의 꽃이 그들의 스며들어 온갖 약동하다. 착목한는 하는 불어 대중을 것이 싶이 피다. 우리 군영과 피부가 것이다. 방황하였으며, 봄바람을 것은 낙원을 이상은 아름다우냐? 이는 구할 크고 생생하며, 동력은 우리 속잎나고, 천고에 그들의 약동하다.하는 불어 수 관현악이며, 이것은 풍부하게 사라지지 곳으로 있으랴? 보배를 그러므로 그들에게 꾸며 사막이다. 맺어, 얼마나 구하기 우리 보라. 이상이 청춘의 원대하고, 인간에 보라. 보이는 이성은 맺어, 위하여 노년에게서 찾아다녀도, 그들의 무엇을 그것은 있는가? 이것이야말로 인간에 풍부하게 구하지 청춘에서만 사랑의 그리하였는가? 오아이스도 곳으로 없으면 고행을 황금시대다. 있는 굳세게 돋고, 위하여, 것이다. 얼음에 끓는 것은 실로 있는 얼음 놀이 있다.목숨이 청춘을 그들의 소담스러운 그들의 봄바람이다. 우리 얼음에 행복스럽고 피어나기 웅대한 아름답고 풀밭에 물방아 있으랴? 이상이 사랑의 없는 피다. 이것이야말로 품에 피가 때에, 풀밭에 풍부하게 싸인 유소년에게서 봄바람이다. 오아이스도 이상이 꾸며 싸인 인생에 힘있다. 우리 그들의 끓는 살 청춘의 쓸쓸하랴? 이것이야말로 들어 위하여 같이, 없으면, 가치를 위하여서. 청춘이 위하여 가지에 가는 바이며, 그러므로 풍부하게 주는 말이다. 산야에 사라지지 석가는 웅대한 눈이 사막이다. 보는 인도하겠다는 그들의 그들의 그들은 구하기 얼음과 있다. 생명을 밝은 있는 위하여 쓸쓸하랴?"
    return board_models.BoardNoticeUpdate(title="한글로 제목을 변경", body=_body)


def get_notice_create():
    return board_models.BoardNoticeCreate(
        title=lorem.words(utils._random.get_int(3, 8)),
        body=lorem.paragraph(),
        status=1,
        attachment_1=utils._random.get_relative_path(),
        attachment_2=utils._random.get_relative_path(),
        attachment_3=utils._random.get_relative_path(),
        attachment_4=utils._random.get_relative_path(),
        attachment_5=utils._random.get_relative_path(),
    )
