from typing import List, Optional
from fastapi import (
    Depends,
    File,
    HTTPException,
    status,
    APIRouter,
    UploadFile,
    Query,
)
from pydantic import EmailStr

from router.backend import dependencies
from core.config import settings
import schemas
import models

router = APIRouter()


@router.post("/send_email")
async def send_mail(
    subject: str = Query(..., title="제목"),
    body_title: str = Query(..., title="본문 제목"),
    body: str = Query(..., title="본문"),
    to_email: EmailStr = Query(..., title="받는 사람 이메일"),
    # TODO: 이메일 인증이 필요하기 때문에 보내는 이메일 주소를 현재를 설정할 수 없다.
    # from_email: EmailStr = Query(...),
    attachments: List[UploadFile] = File(
        None, title="첨부파일", description="첨부파일은 20MB 이하로 하시기 바랍니다."
    ),
    contents: Optional[str] = Query(None, title="추가 컨텐츠"),
    _: models.User = Depends(dependencies.get_admin_usergroup),
):
    """
    Send email
    """

    # setdgrid api key 와 api key가 세팅되어 있어야 한다.
    if not settings.SENDGRID_CHECKING or not settings.SENDGRID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sendgrid config is not set.",
        )

    # dynamic template
    dt = schemas.DynamicTemplate(
        subject=subject,
        body_title=body_title,
        body=body,
    )

    # 추가 contents를 입력되는 경우
    if contents is not None:
        dt.contents = contents

    # dynamic email
    de = schemas.DynamicEmail(to_email=to_email, template=dt)

    # contents변수는 auth템플릿에서만 사용할 수 있다.
    if contents is not None:
        de.template_id = settings.SENDGRID_AUTH_TEMPLATE

    # 첨부파일이 있는 경우
    await de.set_attachments(attachments)

    # 메일전송
    r = de.send_email()

    # 전송 실패시 에러메시지를 리턴한다.
    if r.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(
            status_code=r.status_code,
            detail=r.reason,
        )

    # 성공시 성공 메시지를 리턴한다.
    return {"message": "success"}
