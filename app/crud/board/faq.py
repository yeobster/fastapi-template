# base
from crud.board import BoardCRUDBase, BoardReplyCRUDBase

# post
from models.boards.faq import BoardFaq as Model
from models.boards.faq import BoardFaqCreate as CreateModel
from models.boards.faq import BoardFaqUpdate as UpdateModel

# reply
from models.boards.faq import BoardFaqReply as ReplyModel
from models.boards.faq import BoardFaqReplyCreate as ReplyCreateModel
from models.boards.faq import BoardFaqReplyUpdate as ReplyUpdateModel


class CRUD(BoardCRUDBase[Model, CreateModel, UpdateModel]):
    pass


class ReplyCRUD(
    BoardReplyCRUDBase[ReplyModel, ReplyCreateModel, ReplyUpdateModel]
):
    pass


faq = CRUD(Model)
faq_reply = ReplyCRUD(ReplyModel)
