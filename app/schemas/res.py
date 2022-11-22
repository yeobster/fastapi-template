### response schemas ###
from typing import Any
from pydantic import BaseModel


class RemoveRowResult(BaseModel):
    id: Any
    result: bool = True
