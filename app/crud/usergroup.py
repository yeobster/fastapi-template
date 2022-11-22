from crud.base import CRUDBase

# model
from models.usergroup import UserGroup as Model
from models.usergroup import UserGroupCreate as CreateModel
from models.usergroup import UserGroupUpdate as UpdateModel


class CRUD(CRUDBase[Model, CreateModel, UpdateModel]):
    pass


usergroup = CRUD(Model)
