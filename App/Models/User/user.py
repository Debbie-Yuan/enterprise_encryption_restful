from App.ext import db
from App.Models import UserModelWithPC, Permission


class User(UserModelWithPC):

    # 从BaseModel中继承了 id
    # 从BaseUserModel中继承了 name, _password, is_delete
    # 从UserModelWithPC中继承了permission 和 check_permission 方法

    gender = db.Column(db.String(2))
    is_super = db.Column(db.Boolean(), default=False)
    address = db.Column(db.String(128), default='')
    e_mail = db.Column(db.String(128))
    phone = db.Column(db.String(16))

    def __repr__(self):
        return "User(id={}, name={!r})".format(self.id, self.name)

    @staticmethod
    def create_admin(**kwargs):
        username = kwargs.get('username')
        address = kwargs.get('address')
        gender = kwargs.get('gender')
        e_mail = kwargs.get('email')
        phone = kwargs.get('phone')
        password = kwargs.get('password')
        user = User(
            permission=Permission.grant_super_code(),
            address=address,
            gender=gender,
            e_mail=e_mail,
            phone=phone,
            is_super=True,
            name=username
        )
        user.password = password
        return user
