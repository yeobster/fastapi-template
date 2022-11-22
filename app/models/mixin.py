from typing import Dict, Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Column, TEXT
from schemas.status import Status

TEXT_SIZE = 65535
UNIQUE: Dict = {"unique": True}
TEXT_COLUMN: Dict = {"sa_column": Column(TEXT)}


class DatetimeMixIn(SQLModel):
    """
    생성일과 수정일
    """

    created_at: str = Field(
        ..., max_length=13, title="생성일", description="Linux timestamp"
    )
    updated_at: str = Field(
        None, max_length=13, title="수정일", description="Linux timestamp"
    )


class AttachmentGroupMixin(SQLModel):
    """
    사용자 첨부파일들
    """

    attachment_1: Optional[str] = Field(None, max_length=255, title="첨부파일1")
    attachment_2: Optional[str] = Field(None, max_length=255, title="첨부파일2")
    attachment_3: Optional[str] = Field(None, max_length=255, title="첨부파일3")
    attachment_4: Optional[str] = Field(None, max_length=255, title="첨부파일4")
    attachment_5: Optional[str] = Field(None, max_length=255, title="첨부파일5")


class AgreeMixIn(SQLModel):
    """
    서비스약관 및 개인정보보호 동의
    """

    agree_terms: bool = Field(default=False, title="약관동의")
    agree_private: bool = Field(default=False, title="개인 정보보호 동의")


class StatusMixIn(SQLModel):
    """
    상태
    """

    status: int = Field(
        default=Status.temporary,
        title="상태",
        description="1: Active, 2: Inactive, 3: Temporary",
    )


class AuthorizationMixIn(StatusMixIn):
    """
    인증
    """

    is_authorized: bool = Field(
        default=False,
        title="계정 승인 여부",
        description="이메일 인증이 되었는지 여부. 모든 계정은 이메일 인증 후에 사용가능.",
    )


class AccountMixIn(SQLModel):
    """
    계정정보
    """

    email: EmailStr = Field(
        sa_column_kwargs=UNIQUE,
        index=True,
        title="이메일",
        description="이메일 주소는 관리자 계정과 사용자계정에서 중복사용 불가.",
    )
    name: Optional[str] = Field(max_length=60, title="성명")
    nickname: str = Field(max_length=60, title="별명")
    photo: Optional[str] = Field(
        None,
        max_length=120,
        title="사진경로",
        description="예) /users/1/images/profile.jpg",
    )
    phone: Optional[str] = Field(None, max_length=20, title="연락처")  #  연락처


class AccountPrivateMixIn(SQLModel):
    """
    계정 개인정보
    """

    password: str = Field(max_length=60)  # 비밀번호


class CorpMixIn(SQLModel):
    """
    회사정보
    """

    corp: Optional[str] = Field(None, max_length=60)  # 회사명
    team: Optional[str] = Field(None, max_length=60)  # 부서명
    position: Optional[str] = Field(None, max_length=60)  # 직급


class PostMixIn(SQLModel):
    """
    게시글
    """

    title: str = Field(max_length=150)  # 제목
    body: str = Field(**TEXT_COLUMN)  # 본문
    status: int = Field(
        default=Status.active,
        title="상태",
        description="1: Active, 2: Inactive, 3: Temporary",
    )


class PostMetaMixIn(SQLModel):
    read_count: int = Field(default=0)  # 읽은 수


class PostAttachmentMixIn(SQLModel):
    """
    첨부파일
    """

    attachment_name: Optional[str] = Field(None, max_length=60)  # 이름
    attachment_path: Optional[str] = Field(None, max_length=150)  # 경로
    attachment_size: Optional[int] = Field(None)  # 크기


class AccountGroupMixIn(SQLModel):
    """
    계정그룹
    """

    name: str = Field(max_length=25, sa_column_kwargs=UNIQUE)  # 그룹 명
    desc: str = Field(max_length=100)  # 그룹 설명
