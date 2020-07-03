from App.Models import db, BaseModel
from .user import User
from datetime import datetime


class UserOpLog(BaseModel):

    datetime = db.Column(db.DateTime, default=datetime.now())
    op_code = db.Column(db.Integer)
    op_by = db.Column(db.Integer, db.ForeignKey(User.id))
    op_content = db.Column(db.String(256), default='')

    # 操作目标属性在一阶段开发中暂不需要 op_target =
