# Tags를 채우면 스웨거UI에서 해당 태그로 묶어 API를 추가해준다.

from fastapi import APIRouter

# routers
from router.backend.v1.endpoints import (
    users,
    auths,
    categories,
    usergroups,
    mailer,
)

# backoffice router
# from router.backend.v1.backoffice_endpoints import base as backoffice_base

# board router
from router.backend.v1.endpoints.boards import base as board_base

# router init
api_router = APIRouter()


################################### backoffice API ######################################
# api_router.include_router(
#     backoffice_base.router, prefix="/backoffice", tags=["backoffice"]
# )


################################### base APIs ##########################################
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(auths.router, prefix="/auths", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(board_base.router, prefix="/boards", tags=["boards"])


api_router.include_router(usergroups.router, prefix="/usergroups", tags=["usergroups"])
api_router.include_router(mailer.router, prefix="/mailer", tags=["mailer"])
