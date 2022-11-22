# std
from distutils.util import strtobool
from functools import lru_cache

# third party
from pydantic import BaseModel
from sqlmodel import create_engine, Session
from sqlalchemy.future import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlmodel import text as _text

# user defined
from core.config import settings


class MysqlDSN(BaseModel):
    username: str
    password: str
    dbname: str = ""
    driver: str = "pymysql"
    hostname: str = "localhost"
    port: str = "3306"
    uri: str = ""

    def get_uri(self, ssl=False):
        dsn = (
            "mysql+"
            + self.driver
            + "://"
            + self.username
            + ":"
            + self.password
            + "@"
            + self.hostname
            + ":"
            + self.port
        )

        if self.dbname != "":
            dsn += "/" + self.dbname

        if ssl is True:
            dsn += "?ssl=true"

        self.uri = dsn

        return dsn


class DB:
    session: Session
    engine: Engine
    dsn: MysqlDSN

    def __init__(
        self,
        dsn: MysqlDSN,
        autocommit: bool = False,
    ) -> None:
        self.dsn = dsn
        self._set_engine()
        self.session = Session(self.engine, autocommit=autocommit)

    def _set_engine(self):
        # echo: sql code log flag
        sql_echo = strtobool(settings.MYSQL_DEBUG)
        enable_ssl = strtobool(settings.MYSQL_ENABLE_SSL)
        connect_args = {}

        if enable_ssl:
            connect_args["ssl_ca"] = (
                settings.BASE_DIR + "/certs/DigiCertGlobalRootG2.crt.pem"
            )

        self.engine = create_engine(
            self.dsn.get_uri(ssl=enable_ssl),
            echo=sql_echo,
            echo_pool=True,
            pool_size=30,  # pool size : connection size
            pool_recycle=360,  # pool recycle : x second 후 connection을 재사용 하겠다. (mysql wait_timeout보다 작아야 함.)
            max_overflow=60,  # max_overflow : 허용된 pool_size이상 들어왔을 때 최대 x개 까지 허용하겠다.
            pool_pre_ping=True,  # pool_pre_ping 일정시간 연결이 없어도 ping을 보내서 연결을 유지.
            pool_timeout=900,
            connect_args=connect_args,
        )

    def _get_scalar_result(self, sql):
        return self.session.scalar(sql)

    def _create_database(self, database, encoding="utf8"):
        # url = copy(make_url(self.dsn.uri))
        query = _text(
            "CREATE DATABASE `{0}` CHARACTER SET = '{1}'".format(
                database, encoding
            )
        )
        with self.engine.connect() as connection:
            connection.execute(query)
            connection.commit()

    def _database_exists(self):
        text = "SELECT 1"
        try:
            return bool(self._get_scalar_result(text))
        except (ProgrammingError, OperationalError):
            return False


@lru_cache
def get_db(dbname=settings.MYSQL_DB) -> DB:
    dsn = MysqlDSN(
        username=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        dbname=dbname,
        hostname=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
    )
    db = DB(dsn=dsn)
    return db


_db = get_db()
