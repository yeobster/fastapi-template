# blkpark-fastapi-TEMPLATE

## Requirements

-   Python 3.10.2
-   FASTAPI 0.87.0
-   SQLModel 0.0.8
-   requirements.txt 참조

## configure Dot env

-   PATH : init/dotenv

```
MYSQL_HOST=0.0.0.0
MYSQL_PORT=3306
MYSQL_USER=blkpark
MYSQL_PASSWORD=Abcd1234!
MYSQL_DB=blkpark-fastapi-local
MYSQL_CHARSET=utf-8
```

## Generator (beta)

한번에 crud, model, router를 세팅해주는 기능

## Quick Start

1. mysql이 이미 올라가 있어야 합니다.
2. mysql에 계정이 있어야 하며 dotenv 설정을 완료해야 합니다.
3. initialize를 통해 database를 생성해야 합니다.

```bash
$ python3.10.2 -m venv .venv
$ source .venv/bin/activate
$ python -m pip install --upgrade pip
$ pip install -r requirements.txt
$ pip install -r dev_requirements.txt
$ python initialize.py
$ python run.py
```

### MAC에서 pycrypto가 gmp.h를 불러오지 못해서 설치되지 않을떄

Error

```bash
...
src/_fastmath.c:36:11: fatal error: 'gmp.h' file not found
      # include <gmp.h>
                ^~~~~~~
      1 error generated.
      error: command '/usr/bin/clang' failed with exit code 1
      [end of output]
...
```

Solution

```bash
$ export "CFLAGS=-I/usr/local/include -L/usr/local/lib"
$ pip install pycrypto
```

## CRUD using SQLModel

1. Create

```python
@app.post("/superusers")
def create_superuser(
    superuser_in: superuser.SuperuserCreate,
    session: Session = Depends(router.dependencies.get_session),
):
    superuser = models.Superuser(**superuser_in.dict())
    session.add(superuser)
    session.commit()
    session.refresh(superuser)
    session.close()

    return superuser
```

2. Get List

```python
@app.get("/superusers")
def get_superuser_list(
    session: Session = Depends(router.dependencies.get_session),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    superusers = session.exec(
        select(models.Superuser).offset(offset).limit(limit)
    ).all()

    return superusers
```

3. Get

```python
@app.get("/superusers/{superuser_id}")
def get_superuser_by_id(
    superuser_id: int,
    session: Session = Depends(router.dependencies.get_session),
):
    superuser = session.get(models.Superuser, superuser_id)

    return superuser
```

4. Patch (Update)

```python
@app.patch("/superusers/{superuser_id}")
def update_superuser_by_id(
    superuser_id: int,
    session: Session = Depends(router.dependencies.get_session),
):
    superuser = session.get(models.Superuser, superuser_id)
    superuser.email = "blkpark@test.com"
    session.add(superuser)
    session.commit()
    session.refresh(superuser)

    return superuser
```

5. Put (Replace All Data)

```python
@app.put("/superusers/{superuser_id}")
def replace_superuser_by_id(
    superuser_id: int,
    session: Session = Depends(router.dependencies.get_session),
):
    superuser = session.get(models.Superuser, superuser_id)

    for k, _ in superuser.dict().items():
        if k == "id":
            continue
        setattr(superuser, k, None)

    superuser.name = "abcd"
    superuser.email = "blkpark@gmail.com"

    session.add(superuser)
    session.commit()
    session.refresh(superuser)

    return superuser
```

6. Delete

```python
@app.delete("/superusers/{superuser_id}")
def delete_superuser_by_id(
    superuser_id: int,
    session: Session = Depends(router.dependencies.get_session),
):

    superuser = session.get(models.Superuser, superuser_id)
    session.delete(superuser)
    session.commit()

    return superuser
```
