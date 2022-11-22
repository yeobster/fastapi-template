# base
from crud.board import BoardCRUDBase, BoardReplyCRUDBase

# post
from models.boards.qa import BoardQa as Model
from models.boards.qa import BoardQaCreate as CreateModel
from models.boards.qa import BoardQaUpdate as UpdateModel

# reply
from models.boards.qa import BoardQaReply as ReplyModel
from models.boards.qa import BoardQaReplyCreate as ReplyCreateModel
from models.boards.qa import BoardQaReplyUpdate as ReplyUpdateModel


class CRUD(BoardCRUDBase[Model, CreateModel, UpdateModel]):
    pass


class ReplyCRUD(
    BoardReplyCRUDBase[ReplyModel, ReplyCreateModel, ReplyUpdateModel]
):
    pass


qa = CRUD(Model)
qa_reply = ReplyCRUD(ReplyModel)
