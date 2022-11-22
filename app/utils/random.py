import random, string, time
from typing import List, Union, Tuple
from lorem_text import lorem
from random_word import RandomWords

from .dummy_names import (
    POSITION_LIST,
    BRAND_LIST,
    TEAM_LIST,
    KOREAN_LAST_NAMES,
    KOREAN_FIRST_NAMES,
)


def get_float(start_number: int, end_number: int) -> float:
    """
    시작 숫자와 끝 숫자 사이의 랜덤한 float를 만들어주는 함수
    """
    return float(random.uniform(start_number, end_number))


def get_int(start_number: int, end_number: int) -> int:
    """
    시작 숫자와 끝 숫자 사이의 랜덤한 int를 만들어주는 함수
    """
    return random.randint(start_number, end_number)


def get_index(arr: Union[List, Tuple]) -> int:
    """
    튜플이나 리스트의 랜덤index를 리턴한다.

    Args:
        arr (Union[List, Tuple]): [description]

    Returns:
        int: [description]
    """
    return get_int(0, len(arr) - 1)


def get_string(
    letters_count: int, digits_count: int, is_lowercase=False
) -> str:
    """
    글자수와 숫자 수에 맞춰 랜덤 String을 만들어 주는 함수
    """
    sample_str = "".join(
        (random.choice(string.ascii_letters) for i in range(letters_count))
    )
    sample_str += "".join(
        (random.choice(string.digits) for i in range(digits_count))
    )

    sample_list: List = list(sample_str)
    random.shuffle(sample_list)
    final_string: str = "".join(sample_list)

    if is_lowercase:
        final_string = final_string.lower()

    return final_string


def get_domain() -> str:
    return get_string(10, 0, True) + ".com"


def get_hostname() -> str:
    return "www" + get_domain()


def get_url(path=None, query=None) -> str:
    """
    URL (Uniform Resource Locator)
    http://www.example.com:8080/api/v1?search=blkpark
    mailto:blkpark@blkpark.com

    Protocol or scheme	        http://
    Host or Hostname	        www.example.com:8080
    Subdomain               	www.
    Domain/Domain Name      	example.com
    Port                        8080

    Path                    	/api/v1
    Query                       search=blkpark
    Parameter               	search
    Parameter Value         	blkpark
    """
    url = "http://" + get_hostname()
    if path is None:
        url = url + path

    if query is None:
        url = url + query

    return url


def get_email(domain: str = None) -> str:
    if domain is None:
        domain = get_domain()
    return get_string(5, 2, True) + "@" + domain


def get_phone_number() -> str:
    return "010" + get_string(0, 4) + get_string(0, 4)


def get_relative_path() -> str:
    return "/" + get_string(4, 4) + "/" + get_string(4, 4)


def get_korean_name() -> str:
    return random.choice(KOREAN_LAST_NAMES) + random.choice(KOREAN_FIRST_NAMES)


def get_position() -> str:
    return random.choice(POSITION_LIST)


def get_brand() -> str:
    return random.choice(BRAND_LIST)


def get_team() -> str:
    return random.choice(TEAM_LIST)


def get_word() -> str:
    retry_counter = 0
    max_retry = 5

    while True:
        retry_counter += 1

        if max_retry < retry_counter:
            raise Exception("단어 요청 실패")

        w = RandomWords().get_random_word()
        if w is not None:
            return w

        time.sleep(5)


def get_nickname() -> str:
    w = get_word()
    i = str(get_int(1, 100))
    return w + i
