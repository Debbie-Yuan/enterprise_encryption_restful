from App.Models import db, BaseModel
from .user import User


class PortraitRecords(BaseModel):

    staff_id = db.Column(db.Integer, db.ForeignKey(User.id))
    staff_portrait_prefix = db.Column(db.String(256), default='')
    staff_portrait_amt = db.Column(db.Integer, default=0)


class PortraitFileNames(BaseModel):

    staff_id = db.Column(db.Integer, db.ForeignKey(User.id))
    staff_portrait_md5 = db.Column(db.String(32), nullable=False)
