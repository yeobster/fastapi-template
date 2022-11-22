# std
import uvicorn

# user defined
from core.config import Settings

settings = Settings()

if __name__ == "__main__":
    # run fastapi using uvicorn
    uvicorn.run(
        "main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        log_level=settings.FASTAPI_LOG_LEVEL,
        reload=settings.FASTAPI_RELOAD,
        debug=settings.FASTAPI_DEBUG,
    )
