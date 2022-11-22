import time
from loguru import logger


def wait_sleep_time(sleep_time: int, interval_sec: int = 60):
    """
    sleep_minutes 만큼 sleep
    """

    for i in range(1, sleep_time):
        hours = str(i / 60)
        minutes = str(i % 60)
        logger.debug(f"{hours} hours + {minutes} min 경과")

        # sleep
        time.sleep(secs=interval_sec)
