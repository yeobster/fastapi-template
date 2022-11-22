### constants ###
# run constant
from os import path
from pydantic import BaseConfig


class ENV(BaseConfig):
    LOCAL: str = "local"
    DEV: str = "dev"
    NIGHTLY: str = "nightly"
    LIVE: str = "live"


BASE_DIR: str = path.dirname(path.dirname(path.abspath(__file__)))
AST: str = "['*']"
_env = ENV()
