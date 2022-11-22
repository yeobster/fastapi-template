# core
from crud.base import CRUDBase

# model
from models.diagnoses import Diagnoses as Model
from models.diagnoses import DiagnosesCreate as CreateModel
from models.diagnoses import DiagnosesUpdate as UpdateModel


class CRUD(CRUDBase[Model, CreateModel, UpdateModel]):
    """
    Diagnoses CRUD
    """

    pass


diagnoses = CRUD(Model)