import base64
from typing import List, Optional
from pydantic import EmailStr, BaseModel
from fastapi import UploadFile, HTTPException
import sendgrid
from sendgrid.helpers.mail import (
    Email,
    To,
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
)
from python_http_client import exceptions


from core.config import settings


class DynamicTemplate(BaseModel):
    """
    sendgrid dynamic template에 커스텀하게 설정한 변수
    공통으로 사용중
    """

    subject: str
    body_title: str
    body: str
    contents: Optional[str] = None


class DynamicEmail:
    """
    Dynamic Template을 이용하여 이메일을 보낸다.
    """

    to_email: EmailStr
    subject: str
    template: DynamicTemplate
    template_id: str
    sender: EmailStr
    attachments: List[Attachment] = []

    def __init__(
        self,
        to_email,
        template,
        template_id=None,
        sender=None,
    ):
        if not settings.SENDGRID_CHECKING and not settings.SENDGRID_API_KEY:
            raise Exception("please set sendgrid config.")

        self.to_email = to_email
        self.template = template

        # set default value
        if template_id is None:
            self.template_id = settings.SENDGRID_BASE_TEMPLATE
        else:
            self.template_id = template_id

        # set default value
        if sender is None:
            self.sender = settings.SENDGRID_EMAIL_SENDER
        else:
            self.sender = sender

    async def set_attachment(self, attachment: UploadFile):

        encoded = base64.b64encode(attachment).decode()
        encoded = FileContent(encoded)

        a = Attachment(
            file_content=encoded,
            file_name=FileName(attachment.filename),
            file_type=FileType(attachment.content_type),
        )

        self.attachments.append(a)

    async def set_attachments(self, attachments: List[UploadFile]):
        max_size = 20000000  # 20MB
        sum_size = 0

        for attachment in attachments:
            data = await attachment.read()
            sum_size += len(data)

            if sum_size >= max_size:
                raise HTTPException(
                    status_code=413,
                    detail="attachments size is too large.",
                )

            encoded = base64.b64encode(data).decode()
            encoded = FileContent(encoded)

            a = Attachment(
                file_content=encoded,
                file_name=FileName(attachment.filename),
                file_type=FileType(attachment.content_type),
            )

            self.attachments.append(a)

    def send_email(self) -> bool:

        to_email = To(self.to_email)
        from_email = Email(self.sender)

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
        )

        message.dynamic_template_data = self.template.dict()
        message.template_id = self.template_id

        if len(self.attachments) > 0:
            for attachment in self.attachments:
                message.add_attachment(attachment)

        sendgrid_client = sendgrid.SendGridAPIClient(
            api_key=settings.SENDGRID_API_KEY
        )

        try:
            r = sendgrid_client.send(message)
            return r

        except exceptions.HTTPError as e:
            raise HTTPException(status_code=e.status_code, detail=e.reason)
