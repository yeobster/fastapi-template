# BLKPARK-FASTAPI

## TREE

```bash
├── Dockerfile
├── README.md
└── app
    ├── README.md
    ├── core
    │   ├── __init__.py
    │   ├── config.py
    │   ├── constant.py
    │   ├── db.py
    │   ├── func.py
    │   ├── mailer
    │   │   ├── __init__.py
    │   │   ├── password.py
    │   │   └── signup.py
    │   └── security.py
    ├── crud
    │   ├── __init__.py
    │   ├── base.py
    │   ├── board
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── base_reply.py
    │   │   ├── faq.py
    │   │   ├── notice.py
    │   │   └── qa.py
    │   ├── diagnoses.py
    │   ├── superuser.py
    │   ├── user.py
    │   └── usergroup.py
    ├── dev_requirements.txt
    ├── generator.py
    ├── init
    │   ├── __init__.py
    │   ├── aws.py
    │   ├── database.py
    │   └── dotenv
    │       ├── dev
    │       ├── live
    │       ├── load.py
    │       └── local
    ├── initialize.py
    ├── main.py
    ├── models
    │   ├── __init__.py
    │   ├── base.py
    │   ├── boards
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── faq.py
    │   │   ├── notice.py
    │   │   └── qa.py
    │   ├── diagnoses.py
    │   ├── mixin.py
    │   ├── superuser.py
    │   ├── user.py
    │   ├── usergroup.py
    │   └── usermeta.py
    ├── requirements.txt
    ├── router
    │   └── backend
    │       ├── __init__.py
    │       ├── dependencies.py
    │       └── v1
    │           ├── api.py
    │           ├── backoffice_endpoints
    │           │   ├── __init__.py
    │           │   ├── auths.py
    │           │   ├── base.py
    │           │   └── superusers.py
    │           └── endpoints
    │               ├── auths.py
    │               ├── boards
    │               │   ├── __init__.py
    │               │   ├── base.py
    │               │   ├── faq.py
    │               │   ├── notice.py
    │               │   └── qa.py
    │               ├── categories.py
    │               ├── diagnoses.py
    │               ├── mailer.py
    │               ├── usergroups.py
    │               ├── users.py
    │               └── utilities.py
    ├── run.py
    ├── schemas
    │   ├── __init__.py
    │   ├── mail.py
    │   ├── msg.py
    │   ├── res.py
    │   ├── status.py
    │   ├── token.py
    │   └── usergroup.py
    ├── static
    ├── template
    │   ├── __init__.py
    │   ├── base.py
    │   ├── crud.template
    │   ├── crud__init__.template
    │   ├── model.template
    │   ├── models__init__.template
    │   └── router.template
    ├── tests
    │   ├── __init__.py
    │   ├── base.py
    │   ├── board_base.py
    │   ├── test_faq.py
    │   ├── test_notice.py
    │   ├── test_qa.py
    │   ├── test_user.py
    │   └── test_usergroup.py
    └── utils
        ├── __init__.py
        ├── cls.py
        ├── common.py
        ├── datetime.py
        ├── dummy_names.py
        ├── iso_3166_korean.py
        ├── random.py
        ├── sleep.py
        └── string.py
```

## TODOs

-   ~~Base Project architecture for [FastAPI](https://fastapi.tiangolo.com/ko/)~~
-   ~~support [Python 3.10.2](https://docs.python.org/ko/3/whatsnew/index.html)~~
-   ~~authorization: [JWT]()~~
-   DB support (~~[MYSQL](https://www.mysql.com/)~~, [MongoDB](https://www.mongodb.com/))
-   DB initialize (~~[MYSQL](https://www.mysql.com/)~~, [MongoDB](https://www.mongodb.com/))
-   ~~model base : using [SQLModel](https://sqlmodel.tiangolo.com/)~~
-   ~~CRUD base~~
-   ~~utils~~
-   ~~mailer~~
-   ~~superuser~~
-   usergroup
-   user
-   cookie-cutter
-   alembic
-   Docker
-   Auto Board Maker
-   Generate([Jinja2](https://jinja.palletsprojects.com/en/3.0.x/)) : CRUD, model, router 자동 생성기
    -   ~~CRUD~~
    -   ~~model~~
    -   router(미완성) : 기본적인 기능만 가능. router v1 밑에 기본 API생성이 되나 위치변경필요.
-   ~~multi dotenv~~

## Log Level

TRACE : 추적 레벨은 Debug보다 좀더 상세한 정보를 나타냄
DEBUG : 프로그램을 디버깅하기 위한 정보 지정
INFO : 상태변경과 같은 정보성 메시지를 나타냄
WARN : 처리 가능한 문제, 향후 시스템 에러의 원인이 될 수 있는 경고성 메시지를 나타냄
ERROR : 요청을 처리하는 중 문제가 발생한 경우
FATAL : 아주 심각한 에러, 시스템적으로 심각한 문제
