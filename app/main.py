# std
import time
from ast import literal_eval

# third party libraries.
import sentry_sdk
from loguru import logger
from sqlmodel import text

# fastapi
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from router.backend.v1.api import api_router as v1_backend_router

# user defined libraries
import utils
from core import constant
from core.config import settings, RUN_ENV
from core.db import _db


### initialize ###

# sendgrid(email sender)
if settings.SENDGRID_CHECKING:
    sentry_sdk.init(dsn=settings.SENTRY_DSN)

# set version
version = settings.APP_VERSION

# nightly version set
if RUN_ENV != "local":
    version = version + "-" + RUN_ENV

# init fastapi
app = FastAPI(
    version=version,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# on event #
@app.on_event("startup")
async def startup_event():
    """
    FASTAPI startup event
    """

    logger.debug(
        f"\n[FASTAPI startup event]\nRUN_ENV: {RUN_ENV}\nFASTAPI_DEBUG: {settings.FASTAPI_DEBUG}"
    )

    with _db.engine.connect() as conn:

        # create textual object and execute sql
        with conn.begin():
            sql = "SHOW TABLES"
            stmt = text(sql)
            r = conn.execute(stmt)

            if settings.FASTAPI_DEBUG == True:
                # 디버그 상태에만 출력
                tables = ""
                for table in r:
                    tables = tables + "," + table[0]

                logger.debug(
                    f"\n[MYSQL Info]\n{_db.dsn}\n[Awake DB Query]\nQuery: {sql}\nResult: {tables[1:]}"
                )


@app.on_event("shutdown")
def shutdown_event():
    """
    FASTAPI shutdown event
    """
    logger.critical(
        " -------------------------FASTAPI shutdown event-------------------------"
    )


# middlewares #


# "['*']" -> ["*"]
asterisk = literal_eval(constant.AST)

app.add_middleware(
    CORSMiddleware,
    allow_origins=asterisk,
    allow_credentials=True,
    allow_methods=asterisk,
    allow_headers=asterisk,
)


@app.middleware("http")
async def sentry_exception(req: Request, call_next):
    """
    send sentry
    """

    try:
        res = await call_next(req)
        return res
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_context("req", req)
            scope.user = {
                "ip": req.client.host,
                "header": req.headers,
            }
            logger.critical(e)
            logger.critical(req.headers)
            sentry_sdk.capture_exception(e)
        raise e


@app.middleware("http")
async def log_requests(req: Request, call_next):
    """
    logging requests
    """

    try:
        res: Response = await call_next(req)

        # router dependency를 통하지 않은 경우 init
        if not "request-id" in res.headers:
            res.headers[
                "request-id"
            ] = utils._datetime.get_current_linux_timestamp() + utils._random.get_string(
                5, 0
            )

        if not "start-time" in res.headers:
            res.headers["start-time"] = str(time.time())

        # set idem
        idem = res.headers["request-id"]

        # set start time
        start_time = float(res.headers["start-time"])

        # 헤더에서 start-time 삭제
        del res.headers["start-time"]

        # 시간 계산
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = f"{0:.2f}".format(process_time)

        # logging
        logger.debug(
            f'RID:({idem}) - "{req.method} {req.url.path} {formatted_process_time}ms" - HEADERS = {req.headers} QUERY={req.query_params} PATH={req.path_params}'
        )

        # ex: settings.FASTAPI_CORS_ORIGINS = "['*']"
        res.headers["Access-Control-Allow-Origin"] = literal_eval(
            settings.FASTAPI_CORS_ORIGINS
        )[0]

        return res

    except Exception as e:
        raise e


async def log_body_json(req: Request, res: Response):
    """
    헤더에 content가 있으면 출력, response header에 request-id 항상 전달
    """

    # make request id
    idem = (
        utils._datetime.get_current_linux_timestamp()
        + utils._random.get_string(5, 0)
    )

    # get now
    now = time.time()

    # init response header
    res.headers["request-id"] = idem
    res.headers["start-time"] = str(now)

    # print body
    if "content-length" in req.headers:
        req_header = int(req.headers["content-length"])
        if req_header > 0:
            req_body = await req.json()
            logger.debug(f"RID:{idem} BODY = {req_body}")


# routers #
@app.get("/")
def health_check():
    """health check"""
    return "health-checked"


app.include_router(
    v1_backend_router,
    prefix=settings.API_V1_STR,
)
