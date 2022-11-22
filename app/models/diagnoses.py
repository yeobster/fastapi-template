# user defined
from models.base import ModelBase


### models ###


class DiagnosesBase(ModelBase):
    pass


class DiagnosesCreate(DiagnosesBase):
    """생성 객체"""

    pass


class DiagnosesUpdate(DiagnosesBase):
    """업데이트 객첵"""

    pass


class DiagnosesPublicRead(DiagnosesBase):
    """공개 정보"""

    id: int


class DiagnosesPrivateRead(
    DiagnosesPublicRead
):
    """비공개 정보"""
    pass


# 주의: 마지막 파라메터부터 컬럼이 생성됨
class Diagnoses(
    DiagnosesBase,
    ModelBase,
    table=True,
):
    """
    diagnoses Table
    """

    pass