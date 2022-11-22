# std lib
from distutils.util import strtobool
from functools import lru_cache
from os import getenv
from typing import Optional
from loguru import logger

# third party lib
from pydantic import (
    BaseSettings,
    EmailStr,
    HttpUrl,
)

from core.constant import BASE_DIR, AST, _env
from init.dotenv.load import load_environments

################################################################################
# default settings
################################################################################
RUN_ENV: str = getenv("RUN_ENV", _env.LOCAL)
DEFAULT_SUPERUSER_EMAIL: EmailStr = getenv(
    "DEFAULT_SUPERUSER_EMAIL", "blkpark@blkpark.com"
)
DEFAULT_PASSWORD: str = getenv("DEFAULT_PASSWORD", "Abcd1234!")
DEFAULT_PROJECT_NAME: str = getenv(
    "DEFAULT_PROJECT_NAME", "blkpark-fastapi-TEMPLATE"
)
DEFAULT_EMAIL_SENDER: EmailStr = getenv("DEFAULT_EMAIL_SENDER")
DEFAULT_SECRET_KEY: str = getenv(
    "DEFAULT_SECRET_KEY", "Drmhze6EPcv0fN_81Bj-nA"
)


# sender email이 세팅되어 있지 않다면 기본 관리자 이메일을 사용한다.

if DEFAULT_EMAIL_SENDER is None:
    DEFAULT_EMAIL_SENDER = DEFAULT_SUPERUSER_EMAIL


class Settings(BaseSettings):
    """
    기본 세팅값
    BaseSettings는 Config class를 추가하여 env_file에 경로를 지정해주면 .env를 load를 자동으로 한다.
    """

    ###############################################################################
    # Base Settings
    ###############################################################################
    # Project
    BASE_DIR = BASE_DIR
    API_V1_STR: str = "/api/v1"
    APP_VERSION: str = getenv("APP_VERSION", "0.0.1")
    PROJECT_NAME: str = DEFAULT_PROJECT_NAME
    SERVER_HOST: str = getenv("SERVER_HOST", "0.0.0.0")

    # FastAPI Settings
    FASTAPI_HOST: str = getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(getenv("FASTAPI_PORT", "8888"))
    FASTAPI_LOG_LEVEL: str = getenv("FASTAPI_LOG_LEVEL", "error")
    FASTAPI_RELOAD: bool = strtobool(getenv("FASTAPI_RELOAD", "True"))
    FASTAPI_DEBUG: bool = strtobool(getenv("FASTAPI_DEBUG", "False"))
    FASTAPI_CORS_ORIGINS: str = getenv("FASTAPI_CORS_ORIGINS", AST)

    # Sentry
    SENTRY_DSN: Optional[HttpUrl] = getenv("SENTRY_DSN")

    # MYSQL Settings
    MYSQL_HOST: str = getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = getenv("MYSQL_PORT", "3306")
    MYSQL_USER: str = getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = getenv("MYSQL_PASSWORD", DEFAULT_PASSWORD)
    MYSQL_DB: str = getenv("MYSQL_DB", DEFAULT_PROJECT_NAME)
    MYSQL_CHARSET: str = getenv("MYSQL_CHARSET", "utf-8")
    MYSQL_DEBUG = getenv("MYSQL_DEBUG", "False")
    MYSQL_ENABLE_SSL = getenv("MYSQL_ENABLE_SSL", "False")

    # JWT Settings
    # 60 minutes * 24 hours * 7 days * 4weeks = 28 days
    ALGORITHM = "HS256"
    SECRET_KEY: str = DEFAULT_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 * 4
    EMAIL_RESET_TOKEN_EXPIRE_MILLISECOND: int = 48 * 60 * 60 * 1000

    ###############################################################################
    # Init Configurations
    ###############################################################################

    # Administrator and User
    BASE_SUPERUSER_EMAIL: EmailStr = getenv(
        "BASE_SUPERUSER_EMAIL", DEFAULT_EMAIL_SENDER
    )
    BASE_SUPERUSER_PASSWORD: str = getenv(
        "BASE_SUPERUSER_PASSWORD", DEFAULT_PASSWORD
    )

    ###############################################################################
    # 가입 설정
    ###############################################################################
    # 일반유저 가입가능 여부
    USERS_OPEN_REGISTRATION: bool = strtobool(
        getenv("USERS_OPEN_REGISTRATION", "True")
    )
    # 슈퍼유저 가입가능 여부
    SUPERUSERS_OPEN_REGISTRATION: bool = strtobool(
        getenv("SUPERUSERS_OPEN_REGISTRATION", "False")
    )

    ###############################################################################
    # 사용자 가입시 이메일 인증 여부
    ################################################################################
    # 인증토큰 만료시간 세팅
    AUTHENTICATION_TOKEN_EXPIRE_MINUTES: int = (
        60 * 24
    )  # 60 minutes * 24 hours = 1 day

    # 일반유저 가입시 이메일 인증 여부
    AUTHENTICATION_CHECKING: bool = strtobool(
        getenv("AUTHENTICATION_CHECKING", "True")
    )
    # 슈퍼유저 가입시 이메일 인증 여부
    BACKOFFICE_AUTHENTICATION_CHECKING: bool = strtobool(
        getenv("BACKOFFICE_AUTHENTICATION_CHECKING", "True")
    )

    # 인증서버 설정
    AUTHENTICATION_HOST: str = getenv("AUTHENTICATION_HOST", "localhost")
    AUTHENTICATION_PORT: str = getenv("AUTHENTICATION_PORT", str(FASTAPI_PORT))

    # superuser password
    SUPERUSER_PASSWORD_INIT_URL: Optional[HttpUrl] = getenv(
        "SUPERUSER_PASSWORD_INIT_URL"
    )
    # user password
    USER_PASSWORD_INIT_URL: Optional[HttpUrl] = getenv(
        "USER_PASSWORD_INIT_URL"
    )

    ###############################################################################
    # CLOUD SETTINGS
    ###############################################################################
    # AWS
    AWS_ACCESS_KEY_ID: str = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION: str = getenv("AWS_DEFAULT_REGION", "ap-northeast-2")
    AWS_FILEBUCKET_PATH: HttpUrl = getenv("AWS_FILEBUCKET_PATH")

    # AZURE

    # NAVER OPEN API
    NAVER_OPEN_API_CLIENT_ID: str = getenv("NAVER_OPEN_API_CLIENT_ID")
    NAVER_OPEN_API_CLIENT_SECRET: str = getenv("NAVER_OPEN_API_CLIENT_SECRET")

    ###############################################################################
    # Sendgrid (email sender)
    # 이메일을 전송하는데 사용되는 api key를 설정해야 하며,
    # single sender verification을 사용하여 전송하는 메일주소를 인증해야 한다.
    # dynamic template를 사용하여 구현되어 있다.
    # 기본정보 다이나믹 템플릿은 각각 id를 가지고 있다.(example : d-abcdefg)
    # SENDGRID_BASE_TEMPLATE, SENDGRID_AUTH_TEMPLATE 를 sendgrid에 작성해두었다.
    ###############################################################################

    # 메일 전송을 활성화 할것인지 여부
    SENDGRID_CHECKING: bool = bool(
        strtobool(getenv("SENDGRID_CHECKING", "False"))
    )
    # sendgrid test용 api 최대 일 100개까지
    SENDGRID_API_KEY: str = getenv(
        "SENDGRID_API_KEY",
        "",
    )
    SENDGRID_BASE_TEMPLATE: str = getenv(
        "SENDGRID_BASE_TEMPLATE", "d-899797f3a4f64e3db06058bc5e98b62f"
    )
    SENDGRID_AUTH_TEMPLATE: str = getenv(
        "SENDGRID_AUTH_TEMPLATE", "d-c93ed6989bf3467a81d0416c9f6fde1e"
    )  # 인증용 템플릿
    SENDGRID_EMAIL_SENDER: str = getenv(
        "SENDGRID_EMAIL_SENDER", DEFAULT_EMAIL_SENDER
    )

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"


@lru_cache
def load_settings():
    logger.debug(
        "실행 환경변수 파일을 변경하려면 RUN_ENV의 값을 DEV, LOCAL, LIVE, NIGHTLY중 하나를 선택하세요."
    )

    # env set
    load_type = _env.LOCAL

    if RUN_ENV != _env.LOCAL:
        load_type = RUN_ENV

    # load get env
    load_environments(load_type=load_type)
    settings = Settings()

    if settings.FASTAPI_DEBUG == True:
        logger.debug(f"\n[환경변수 정보]\n{settings.dict()}")

    return settings


settings = load_settings()
