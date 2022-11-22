# TODO: 아래 기능은 검증되지 않음. 구현해야함.

from fastapi import APIRouter
from router.backend.v1.backoffice_endpoints import superusers, auths


router = APIRouter()

# TODO: 백오피스 기능 구현 후, 라우터 추가할 것
# router.include_router(
#     superusers.router, prefix="/superusers", tags=["superusers"]
# )

# router.include_router(auths.router, prefix="/auths", tags=["auths"])
