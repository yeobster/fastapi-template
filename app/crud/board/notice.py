# base
from crud.board import BoardCRUDBase, BoardReplyCRUDBase

# post
from models.boards.notice import BoardNotice as Model
from models.boards.notice import BoardNoticeCreate as CreateModel
from models.boards.notice import BoardNoticeUpdate as UpdateModel

# reply
from models.boards.notice import BoardNoticeReply as ReplyModel
from models.boards.notice import BoardNoticeReplyCreate as ReplyCreateModel
from models.boards.notice import BoardNoticeReplyUpdate as ReplyUpdateModel


class CRUD(BoardCRUDBase[Model, CreateModel, UpdateModel]):
    pass


class ReplyCRUD(
    BoardReplyCRUDBase[ReplyModel, ReplyCreateModel, ReplyUpdateModel]
):
    pass


notice = CRUD(Model)
notice_reply = ReplyCRUD(ReplyModel)
