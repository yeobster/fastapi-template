from loguru import logger


def create_usergroup():
    logger.info("유저그룹 생성")


def get_usergroup():
    logger.info("유저그룹 조회")


def get_list_usergroup():
    logger.info("유저그룹 리스트 조회")


def update_usergroup():
    logger.info("유저그룹 수정")


def delete_usergroup():
    logger.info("유저그룹 삭제")


def test_usergroup():
    logger.info("로그인하기")

    get_list_usergroup()
    get_usergroup()
    create_usergroup()
    update_usergroup()
    delete_usergroup()
