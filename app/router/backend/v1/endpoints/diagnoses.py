from typing import List

from fastapi import APIRouter, Depends, Path, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session

import crud, models, schemas
from router.backend import dependencies

router = APIRouter()


@router.post(
    "",
    response_model=models.Diagnoses,
    response_model_exclude=["password"],
    response_model_exclude_none=True,
)
def create_superuser(
    diagnoses_in: models.DiagnosesCreate,
    db: Session = Depends(dependencies.get_session),
    current_user: models.Superuser = Depends(dependencies.get_current_superuser),
) -> models.Diagnoses:
    """
    Diagnoses 생성
    """

    diagnoses = crud.diagnoses.create(db, obj_in=diagnoses_in)

    return diagnoses


@router.get(
    "",
    response_model=List[models.Diagnoses],
    response_model_exclude_none=True,
)
def get_diagnoses_list(
    db: Session = Depends(dependencies.get_session),
    skip: int = 0,
    limit: int = 100,
) -> List[models.Diagnoses]:
    """
    get Diagnoses list
    """

    diagnoses: List[models.Diagnoses] = crud.diagnoses.get_multi(
        db, skip=skip, limit=limit
    )

    return diagnoses


@router.get(
    "/{" + "diagnoses_id" + "}",
    response_model=models.Diagnoses,
    response_model_exclude_none=True,
)
def get_diagnoses_by_id(
    db: Session = Depends(dependencies.get_session),
    diagnoses_id: int = Path(...),
) -> models.Diagnoses:
    """
    get Diagnoses by id
    """

    diagnoses = crud.diagnoses.get(db, _id=diagnoses_id)

    return diagnoses


@router.patch(
    "/{" + "diagnoses_id" + "}",
    response_model=models.Diagnoses,
    response_model_exclude_none=True,
)
def patch_diagnoses_by_id(
    diagnoses_in: models.DiagnosesUpdate,
    db: Session = Depends(dependencies.get_session),
    diagnoses_id: int = Path(...),
) -> models.Diagnoses:
    """
    update Diagnoses by id
    """

    diagnoses = crud.diagnoses.get(db, _id=diagnoses_id)

    if diagnoses is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="diagnoses_id를 찾을 수 없습니다."
        )

    diagnoses = crud.diagnoses.update(db, db_obj=diagnoses, obj_in=diagnoses_in)

    return diagnoses


@router.get(
    "/{diagnoses_id}/reports",
    response_model=models.Diagnoses,
    response_model_exclude_none=True,
)
def get_diagnosis_reports():
    return __name__


@router.get(
    "/{diagnoses_id}/reports/{report_id}",
    response_model=models.Diagnoses,
    response_model_exclude_none=True,
)
def get_diagnosis_report_by_id():
    return __name__
