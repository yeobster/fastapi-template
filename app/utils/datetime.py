# Date와 Time에 관련된 공통함수들.

import time


def get_eng_month_string(_month_int: int, lower_string: bool = False) -> str:

    eng = (
        "Jan.",
        "Feb.",
        "Mar.",
        "Apr.",
        "May.",
        "Jun.",
        "Jul.",
        "Aug.",
        "Sep.",
        "Oct.",
        "Nov.",
        "Dec.",
    )

    if _month_int < 1:
        return ""

    if _month_int > 12:
        return ""

    r = eng[_month_int - 1]
    if lower_string:
        r = r.lower()

    return r


def get_current_linux_timestamp() -> str:
    """
    타임스탬프 값을 스트링으로 리턴하게 해주는 함수
    """
    return str(int(time.time() * 1000))
