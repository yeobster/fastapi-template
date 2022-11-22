import json
from typing import Any, Literal
import urllib.request

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from core.config import settings
from router.backend import dependencies

router = APIRouter()


@router.post("/test-email", response_model=schemas.Msg, status_code=201)
def test_email(
    # email_to: EmailStr,
    # current_user: models.Users = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    subject = "[BLKPARK] test mail 입니다"
    body_title = "Lorem Ipsum"
    body = "모든 국민은 근로의 의무를 진다. 국가는 근로의 의무의 내용과 조건을 민주주의원칙에 따라 법률로 정한다. 이 헌법시행 당시에 이 헌법에 의하여 새로 설치될 기관의 권한에 속하는 직무를 행하고 있는 기관은 이 헌법에 의하여 새로운 기관이 설치될 때까지 존속하며 그 직무를 행한다. 제1항의 지시를 받은 당해 행정기관은 이에 응하여야 한다. 국회의원의 선거구와 비례대표제 기타 선거에 관한 사항은 법률로 정한다. 선거운동은 각급 선거관리위원회의 관리하에 법률이 정하는 범위안에서 하되, 균등한 기회가 보장되어야 한다. 국가안전보장회의의 조직·직무범위 기타 필요한 사항은 법률로 정한다."
    contents = (
        "재산권의 행사는 공공복리에 적합하도록 하여야 한다. 국가원로자문회의의 조직·직무범위 기타 필요한 사항은 법률로 정한다."
    )
    to_email = "blkpark@blkpark.com"

    dt = schemas.DynamicTemplate(
        subject=subject, body_title=body_title, body=body, contents=contents
    )
    de = schemas.DynamicEmail(to_email, dt)
    de.send_email()

    return {"msg": "Test email sent"}


@router.get("/email/duplicate")
def check_duplicate_mail(
    db: Session = Depends(dependencies.get_session), email_in: str = Query(...)
):
    """
    이메일 중복 체크
    """
    user = crud.user.get_by_email(db, email=email_in)
    if user:
        raise HTTPException(
            400,
            detail="이미 해당 메일주소로 가입된 계정이 있습니다.",
        )

    # 관리자로 등록된 이메일이 있는지 체크한다.
    user = crud.superuser.get_by_email(db, email=email_in)
    if user:
        raise HTTPException(
            400,
            detail="이미 해당 메일주소로 가입된 계정이 있습니다.",
        )

    return {"result": False, "desc": "중복되지 않습니다."}


@router.get("/translate", response_model=schemas.Papago)
def translate(
    text: str = Query(...),
    source: Literal[
        "ko",
        "ja",
        "zh-cn",
        "zh-tw",
        "hi",
        "en",
        "es",
        "fr",
        "de",
        "pt",
        "vi",
        "id",
        "fa",
        "ar",
        "mm",
        "th",
        "ru",
        "it",
    ] = Query("ko"),
    target: Literal[
        "ko",
        "ja",
        "zh-cn",
        "zh-tw",
        "hi",
        "en",
        "es",
        "fr",
        "de",
        "pt",
        "vi",
        "id",
        "fa",
        "ar",
        "mm",
        "th",
        "ru",
        "it",
    ] = Query("en"),
):
    """
    일일 요청가능횟수 10000글자
    언어감지 2000000
    """

    if target == source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"소스언어{source}와 타겟언어{target}가 같습니다.다르게 선택해주세요",
        )

    client_id = settings.NAVER_OPEN_API_CLIENT_ID  # 개발자센터에서 발급받은 Client ID 값
    client_secret = (
        settings.NAVER_OPEN_API_CLIENT_SECRET
    )  # 개발자센터에서 발급받은 Client Secret 값

    encText = urllib.parse.quote(text)
    data = "source=" + source + "&target=" + target + "&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    resp = urllib.request.urlopen(req, data=data.encode("utf-8"))
    status_code = resp.getcode()

    if int(status_code / 100) != 2:
        raise HTTPException(status_code=status_code, detail="번역에 실패하였습니다.")

    resp_body = resp.read()
    decoded = resp_body.decode("utf-8")
    loaded = json.loads(decoded)
    translated = loaded["message"]["result"]
    r = schemas.Papago(**translated)
    return r
