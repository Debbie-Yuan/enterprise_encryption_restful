from App.ext import db
from App.Models import BaseModel
from .user import User
from datetime import datetime


class Attendance(BaseModel):

    staff_id = db.Column(db.Integer, db.ForeignKey(User.id))
    check_datetime = db.Column(db.DateTime, default=datetime.now())
