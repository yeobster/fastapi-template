# 데이터베이스를 초기화 하고 models내에 있는 모든 모델을 생성한다.
# Warning: 데이터베이스가 미리 생성되어 있어야 한다.


import sys
from typing import List
from loguru import logger

from sqlmodel import SQLModel, text
from sqlalchemy_utils import database_exists, create_database


# user defined
from core.config import settings
from core import config
from core.db import _db
from core.security import get_password_hash
from init.dotenv.load import load_environments

import models, schemas, utils
from models import boards


def create_database_and_table():
    logger.info("데이터베이스를 생성하고 메타데이터를 생성합니다. :", _db.engine)

    SQLModel.metadata.create_all(bind=_db.engine)
    with _db.engine.connect() as conn:

        # create textual object and execute sql
        with conn.begin():
            sql = "SHOW TABLES"
            logger.info(sql)
            stmt = text(sql)
            tables = conn.execute(stmt)

            # print
            for table in tables:
                logger.info(table)


def init_superuser():
    name = "administrator"
    email = settings.BASE_SUPERUSER_EMAIL
    nickname = "관리자"
    password = get_password_hash(password=settings.BASE_SUPERUSER_PASSWORD)
    now = utils._datetime.get_current_linux_timestamp()

    superuser = models.Superuser(
        name=name,
        email=email,
        nickname=nickname,
        status=schemas.Status.active,
        is_authorized=True,
        password=password,
        created_at=now,
        updated_at=now,
    )
    logger.info(superuser)
    insert_rows([superuser])


def init_usergroup():
    """
    basic
    visitor
    admin
    """
    usergroups = []
    now = utils._datetime.get_current_linux_timestamp()
    usergroups.append(
        models.UserGroup(**schemas.UserGroup.guest, created_at=now)
    )

    usergroups.append(
        models.UserGroup(**schemas.UserGroup.base, created_at=now)
    )

    usergroups.append(
        models.UserGroup(**schemas.UserGroup.admin, created_at=now)
    )
    logger.info(f"{usergroups}")
    insert_rows(usergroups)


def init_base_user():
    now = utils._datetime.get_current_linux_timestamp()
    password = get_password_hash(password=config.DEFAULT_PASSWORD)

    admin_user = models.User(
        name="NoShik Park",
        email="blake@blkpark.com",
        nickname="nspark",
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/3347029?v=4",
        corp="제이펀",
        team="개발팀",
        position="PM",
        password=password,
        user_group_id=schemas.UserGroup.admin["id"],
        agree_terms=True,
        agree_private=True,
        is_authorized=True,
        agreed_at=now,
        status=schemas.Status.active,
        created_at=now,
    )
    admin_user2 = models.User(
        name="Jiwon Jang",
        email="jiwon@blkpark.com",
        nickname="jiwon",
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/10695610?v=4",
        corp="제이펀",
        team="임원",
        position="사원",
        password=password,
        user_group_id=schemas.UserGroup.admin["id"],
        agree_terms=True,
        agree_private=True,
        is_authorized=True,
        agreed_at=now,
        status=schemas.Status.active,
        created_at=now,
    )
    base_user = models.User(
        name="BeomHwan Ham",
        email="beomhwan@blkpark.com",
        nickname="crazyboo",
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/10695610?v=4",
        corp="제이펀",
        team="연구소",
        position="사원",
        password=password,
        user_group_id=schemas.UserGroup.base["id"],
        agree_terms=True,
        agree_private=True,
        is_authorized=True,
        agreed_at=now,
        status=schemas.Status.active,
        created_at=now,
    )
    base_user2 = models.User(
        name="Jihoon Seo",
        email="jihoon@blkpark.com",
        nickname="jihoon",
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/10695610?v=4",
        corp="제이펀",
        team="경영지원팀",
        position="사원",
        password=password,
        user_group_id=schemas.UserGroup.base["id"],
        agree_terms=True,
        agree_private=True,
        is_authorized=True,
        agreed_at=now,
        status=schemas.Status.active,
        created_at=now,
    )

    guest_user = models.User(
        name="DongGeon Jung",
        email="jcargun@blkpark.com",
        nickname="jcargun",
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/86874497?v=4",
        corp="제이펀",
        team="개발팀",
        position="사원",
        password=password,
        user_group_id=schemas.UserGroup.guest["id"],
        agree_terms=True,
        agree_private=True,
        is_authorized=True,
        agreed_at=now,
        status=schemas.Status.active,
        created_at=now,
    )
    guest_user2 = models.User(
        name="JinSung Lee",
        email="jslee@blkpark.com",
        nickname="jslee629",
        phone=utils._random.get_phone_number(),
        photo="https://avatars.githubusercontent.com/u/67567206?v=4",
        corp="제이펀",
        team="개발팀",
        position="사원",
        password=password,
        user_group_id=schemas.UserGroup.guest["id"],
        agree_terms=True,
        agree_private=True,
        is_authorized=True,
        agreed_at=now,
        status=schemas.Status.active,
        created_at=now,
    )
    users = [
        admin_user,
        admin_user2,
        base_user,
        base_user2,
        guest_user,
        guest_user2,
    ]
    logger.info(users)
    insert_rows(users)


def insert_rows(rows: List[SQLModel]):
    """
    기본 유저그룹생성
    """
    for i in rows:
        _db.session.add(i)
        _db.session.commit()
        _db.session.expire(i)


def create_boards():
    """
    기본 게시판 생성
    # TODO: notice, free
    """
    pass


def create():
    create_database_and_table()
    init_usergroup()
    init_superuser()
    init_base_user()

    # create_boards()


def initialize():
    try:
        if not database_exists(_db.engine.url):
            create_database(_db.engine.url, encoding="utf8")
            create()
        else:
            # DB가 존재할 떄
            while True:
                logger.info(f"Engine: {_db.engine}")
                logger.info("모든 테이블을 지우고 새로 생성시겠습니까? [y/n]")
                r = sys.stdin.readline()
                r = r.replace("ㅛ", "y")
                r = r.replace("ㅜ", "n")
                r = r.lower()
                if r == "y\n":
                    logger.info("y")

                    # off 외래키 제약조건
                    query = text("SET FOREIGN_KEY_CHECKS=0")
                    with _db.engine.connect() as conn:
                        conn.execute(query)
                        conn.commit()

                    # model에 등록된 모든 테이블 삭제
                    SQLModel.metadata.drop_all(bind=_db.engine)

                    # on 외래키 제약조건
                    query = text("SET FOREIGN_KEY_CHECKS=1")
                    with _db.engine.connect() as conn:
                        conn.execute(query)
                        conn.commit()

                    create()
                    break
                elif r == "n\n":
                    logger.info("기존 데이터베이스가 유지됩니다. 마이그레이션은 alembic을 사용해주세요")
                    break
                else:
                    logger.info("다시 입력해주세요", r)

    except Exception as e:
        logger.error(e)
        raise e


def run():
    load_environments()
    logger.info("Initializing service..")
    initialize()
    _db.session.close()
    logger.info("Finished!")
