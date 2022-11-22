FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

LABEL maintainer="blake park <blkpark@blkpark.com>"

COPY ./app /app
