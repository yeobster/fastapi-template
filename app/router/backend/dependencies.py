from typing import Any, Union
from sqlmodel import SQLModel, Session

# fastapi
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.db import _db
import schemas, models, crud, core


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auths/login/access-token",
)


def get_session() -> Session:
    """
    get db session

    Yields: session
    """
    with Session(_db.engine) as session:
        yield session


def decode_token(
    token: str = Depends(reusable_oauth2),
) -> schemas.TokenPayloadSub:
    """
    토큰 체크
    """

    payload_sub = core.security.decode_token(token=token)

    return payload_sub


def get_current_user(
    db: Session = Depends(get_session),
    payload_sub: schemas.TokenPayloadSub = Depends(decode_token),
) -> models.User:
    """
    사용자 토큰 인증
    """

    # check scope
    if payload_sub.scope != schemas.Scope.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 잘못되었습니다."
        )

        # find user
    user = crud.user.get(db, _id=payload_sub.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="유저를 찾을 수 없습니다."
        )

    return user


def get_current_superuser(
    db: Session = Depends(get_session),
    payload_sub: schemas.TokenPayloadSub = Depends(decode_token),
) -> models.Superuser:
    """
    관리자 토큰 인증
    """

    # check scope
    if payload_sub.scope != schemas.Scope.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="콘텐츠에 접근할 권리를 가지고 있지 않습니다.",
        )

    # find superuser
    superuser = crud.superuser.get(db, _id=payload_sub.id)
    if not superuser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="유저를 찾을 수 없습니다."
        )

    return superuser


def get_current_active_superuser(
    current_superuser: models.Superuser = Depends(get_current_superuser),
) -> models.Superuser:
    """
    관리자 활성화 체크
    """

    if current_superuser.status != schemas.Status.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"활성화 되어 있지 않은 superuser입니다.(status code: {current_superuser.status})",
        )

    return current_superuser


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    (유저 그룹에 상관없이) 사용자 아이디 활성화 체크
    """
    if current_user.status != schemas.Status.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="비활성화 되어 있는 유저입니다."
        )

    return current_user


def get_current_active_user_in_admin_group(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    사용자 아이디 중 admin user group에서만
    """
    # admin group
    if not is_user_in_admin_group(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="유저그룹을 확인해주세요"
        )

    return current_user


def get_active_user_or_active_superuser(
    db: Session = Depends(get_session),
    payload_sub: schemas.TokenPayloadSub = Depends(decode_token),
) -> Union[models.User, models.Superuser]:
    """
    active한 superuser 또는 user 체크
    """
    _user: Union[models.User, models.Superuser]
    # check scope
    # superuser scope
    if payload_sub.scope == schemas.Scope.superuser:

        # find superuser
        _user: models.Superuser = crud.superuser.get(db, _id=payload_sub.id)
        if _user and _user.status == schemas.Status.active:
            return _user

    # user scope
    if payload_sub.scope == schemas.Scope.user:

        # find user
        _user: models.User = crud.user.get(db, _id=payload_sub.id)
        if _user and _user.status == schemas.Status.active:
            return _user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="접근할 권리를 가지고 있지 않습니다.",
    )


def get_admin_usergroup(
    current_user: Union[models.Superuser, models.User] = Depends(
        get_active_user_or_active_superuser
    ),
) -> Union[models.User, models.Superuser]:
    """
    user의 usergroup이 admin 이거나,
    superuser
    """

    # pass superuser
    if isinstance(current_user, models.Superuser):
        return current_user

    # admin group
    if is_user_in_admin_group(current_user):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="유저그룹을 확인해주세요"
    )


def get_admin_or_base_usergroup(
    current_user: Union[models.Superuser, models.User] = Depends(
        get_active_user_or_active_superuser
    ),
) -> Union[models.User, models.Superuser]:
    """
    user의 usergroup이 admin,base 이거나
    superuser
    """

    # pass superuser
    if isinstance(current_user, models.Superuser):
        return current_user

    # admin group
    if is_user_in_admin_group(current_user):
        return current_user

    # guest group
    if is_user_in_base_group(current_user):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="유저그룹을 확인해주세요"
    )


def get_admin_or_guest_usergroup(
    current_user: Union[models.Superuser, models.User] = Depends(
        get_active_user_or_active_superuser
    ),
) -> Union[models.Superuser, models.User]:
    """
    user의 usergroup이 admin, guest 이거나,
    superuser
    """

    # pass superuser
    if isinstance(current_user, models.Superuser):
        return current_user

    # admin group
    if is_user_in_admin_group(current_user):
        return current_user

    # guest group
    if is_user_in_guest_group(current_user):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="유저그룹을 확인해주세요"
    )


#####  유저그룹 확인 functions #####


def is_user_in_admin_group(_user: models.User) -> bool:
    # admin group
    if _user.user_group_id != schemas.UserGroup.admin["id"]:
        return False

    return True


def is_user_in_base_group(_user: models.User) -> bool:
    # base group
    if _user.user_group_id != schemas.UserGroup.base["id"]:
        return False

    return True


def is_user_in_guest_group(_user: models.User) -> bool:
    # guest group
    if _user.user_group_id != schemas.UserGroup.guest["id"]:
        return False

    return True


def validate_signup_backoffice(
    user_in: models.SuperuserCreate,
    db: Session = Depends(get_session),
) -> models.SuperuserCreate:
    return validate_signup(user_in, db)


def validate_signup_base(
    user_in: models.UserCreate,
    db: Session = Depends(get_session),
) -> models.SuperuserCreate:
    return validate_signup(user_in, db)


def validate_signup(
    user_in: Any,
    db: Session,
) -> SQLModel:
    """
    가입이 가능한지 체크
    """

    # check open registration.
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="공개 가입을 허용하지 않았습니다.",
        )

    # check user email
    if isinstance(user_in, models.UserCreate):
        user: models.User = crud.user.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 해당 메일주소로 가입된 계정이 있습니다. 관리자에게 확인해보세요",
            )

    # check superuser email
    if isinstance(user_in, models.SuperuserCreate):
        superuser = crud.superuser.get_by_email(db, email=user_in.email)
        if superuser:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 해당 메일주소로 가입된 계정이 있습니다. 관리자에게 확인해보세요",
            )

    return user_in


def find_email_in_all_accounts(
    email: str, db: Session = Depends(get_session)
) -> Union[models.Superuser, models.User, None]:
    """
    이메일을 통해 유저를 찾는다.
    """

    user = crud.user.get_by_email(db, email=email)
    if user:
        return user

    superuser = crud.superuser.get_by_email(db, email=email)
    if superuser:
        return superuser

    return None
