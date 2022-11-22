# class와 관련된 공통함수

import inspect
from typing import Tuple, Dict


def get_class_values(obj) -> Tuple:
    """
    class로 선언된 상수값을 Literal로 사용할 수 있게 해주는 함수.

    Usage:
    Literal[get_class_values(Campaign.BidStrategy)]

    Example:
    class FBCampaignBase(BaseModel):
        name: str
        daily_budget: float
        bid_strategy: Literal[get_class_values(Campaign.BidStrategy)]

    Description:
    클래스의 python special variable을 제외하고 멤버들의 값을 가지고 온다.
    페이스북의 클래스들은 BaseModel이 아니기 때문에 fastapi schema를 통해 validation체크를 할 수 없다.
    typing의 Literal을 사용하여 페이스북 SDK에서 선언된 상수값을 Literal으로 사용하여 validation체크를
    할 수 있게 tuple형태로 멤버값을 리턴하는 함수.
    """
    values = []
    attrs = inspect.getmembers(obj, lambda a: not (inspect.isroutine(a)))

    for attr in attrs:
        if attr[0].startswith("__"):
            continue
        if attr[0].endswith("__"):
            continue
        values.append(attr[1])

    return tuple(values)


def get_class_to_dict_without_private_member(cls) -> Dict:

    values: Dict = dict()
    attrs = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))

    for attr in attrs:
        if attr[0].startswith("__"):
            continue
        if attr[0].endswith("__"):
            continue
        if attr[0].startswith("_"):
            continue
        values[attr[0]] = attr[1]

    return values
