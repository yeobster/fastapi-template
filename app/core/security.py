from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from loguru import logger
from fastapi import HTTPException, status

from pydantic import ValidationError


from core.config import settings
import schemas

# bcrypt 설치 필수
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_token(payload_sub: schemas.TokenPayloadSub) -> schemas.Token:
    # 만료시간 세팅
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # create token
    access_token = create_access_token(
        subject=payload_sub.get_subject(), expires_delta=access_token_expires
    )

    token = schemas.Token(access_token=access_token)
    return token


def create_authentication_token(
    token_sub: schemas.TokenPayloadSub,
) -> str:
    # make token
    expires = timedelta(settings.AUTHENTICATION_TOKEN_EXPIRE_MINUTES)
    subject = f"{token_sub.id},{token_sub.scope},{schemas.TokenType.user_authentication}"

    encoded_jwt = create_access_token(subject=subject, expires_delta=expires)

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_password_reset_token(subject: str) -> str:
    delta = timedelta(
        milliseconds=settings.EMAIL_RESET_TOKEN_EXPIRE_MILLISECOND
    )
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": subject},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> schemas.TokenPayloadSub:
    try:
        algorithm = settings.ALGORITHM
        key = settings.SECRET_KEY

        decoded = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        payload = schemas.TokenPayload(**decoded)
        payload_sub: schemas.TokenPayloadSub = payload.parse()

        return payload_sub

    except schemas.TokenSubParseError as e:
        logger.critical(e)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="잘못된 토큰입니다.")

    except jwt.ExpiredSignatureError as e:
        logger.critical(e)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="ExpiredSignatureError"
        )
    except jwt.JWTError as e:
        logger.critical(e)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="JWTError")

    except ValidationError:
        logger.critical(token)
        logger.critical(algorithm)
        logger.critical(key)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ValidationError.",
        )

    except Exception as e:
        raise e


def verify_token_payload_sub(
    token: str, is_superuser: bool = False
) -> schemas.TokenPayloadSub:
    payload_sub: schemas.TokenPayloadSub = decode_token(token=token)
    if payload_sub.token_type is not schemas.TokenType.user_authentication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="토큰타입이 올바르지 않습니다."
        )
    if is_superuser:
        if payload_sub.scope is not schemas.Scope.superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="스코프가 올바르지 않습니다.",
            )

    elif is_superuser is False:
        if payload_sub.scope is not schemas.Scope.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="스코프가 올바르지 않습니다.",
            )
    return payload_sub
