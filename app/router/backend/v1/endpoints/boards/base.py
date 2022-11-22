from fastapi import APIRouter


# from router.v1.endpoints.boards import faq
from router.backend.v1.endpoints.boards import faq, notice, qa


router = APIRouter()

router.include_router(faq.router, prefix="/faq")
router.include_router(notice.router, prefix="/notice")
router.include_router(qa.router, prefix="/qa")
