from werkzeug.security import generate_password_hash, check_password_hash
from App.ext import db
from App.Models.settings import Permission
from sqlalchemy.orm.session import Session


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def save(self):
        try:
            session = db.session
            session.add(self)
            session.commit()
            return True
        except Exception as e:
            print(str(e))
            return False

    def delete(self):
        try:
            session = db.session
            assert isinstance(session, Session)
            session.delete(self)
            session.commit()
            return True
        except Exception as e:
            print(e)
            return False


class BaseUserModel(BaseModel):
    __abstract__ = True

    name = db.Column(db.String(32), unique=True, nullable=False)
    _password = db.Column(db.String(128), nullable=False)
    is_delete = db.Column(db.Boolean(), default=False, nullable=False)
    # 项目扩展性保证，若需要对用户级联，只需要绑定相应id
    extension = db.Column(db.Integer, default=0)

    @property
    def password(self):
        raise LookupError("No Permission to get the PASSWPRD.")

    @password.setter
    def password(self, new_pass_val):
        self._password = generate_password_hash(new_pass_val)

    def check_password(self, input_pass_val):
        return check_password_hash(self._password, input_pass_val)

    def check_permission(self, permission):
        raise NotImplementedError


class UserModelWithPC(BaseUserModel):
    __abstract__ = True

    permission = db.Column(db.Integer, default=Permission.grant_normal_code(), nullable=False)

    def check_permission(self, permission):
        if not hasattr(Permission, permission):
            return False

        return (self.permission & getattr(Permission, permission)) > 0
