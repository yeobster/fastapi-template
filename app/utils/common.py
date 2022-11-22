import os
from pathlib import Path
from loguru import logger


def create_directory(p):
    """
    [desc]
    디렉토리를 생성한다.

    [parameters]
    p: path
    """
    try:
        # not exists
        o = Path(p)
        if not o.exists():
            # if not os.direxists(p):
            os.makedirs(p)
            logger.debug(f"created directory : {p}")
            return p

        else:
            # logger.debug("create_directory passed (already exists)")
            return p

    except OSError:
        logger.critical("ERROR : " + p)
