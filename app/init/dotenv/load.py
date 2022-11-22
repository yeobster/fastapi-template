import sys
from os.path import join
from loguru import logger
from dotenv import load_dotenv

from core.constant import BASE_DIR, _env


def load_environments(load_type=None):

    dotenv_path = BASE_DIR + "/init/dotenv"

    if load_type is None:
        logger.debug("\n[Select Mode]\n1.local\n2.dev\n3.nightly\n4.live")
        logger.debug("\nType Select: ")
        load_type = sys.stdin.readline()
        splited = load_type.split("\n")
        load_type = splited[0].lower()

    if load_type == _env.LOCAL or load_type == "1":
        dotenv_path = join(dotenv_path, "local", ".env")

    elif load_type == _env.DEV or load_type == "2":
        dotenv_path = join(dotenv_path, "dev", ".env")

    elif load_type == _env.NIGHTLY or load_type == "3":
        dotenv_path = join(dotenv_path, "nightly", ".env")

    elif load_type == _env.LIVE or load_type == "4":
        dotenv_path = join(dotenv_path, "live", ".env")

    logger.debug(f"[{load_type}]이(가) 선택되었습니다. 환경설정 파일을 읽어들입니다.({dotenv_path})")

    load_dotenv(dotenv_path=dotenv_path, verbose=True)
