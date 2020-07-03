from flask import g
from flask_restful import Resource, reqparse, fields, marshal, abort

from settings import ApiConstant, TokenPrefix
from App.ext import cache
from App.Models.User import User
from App.utils import generate_token
from App.Apis.api_utils import get_user_by_raw_input, get_user_by_name, get_user_by_email, get_user_by_phone, \
    login_required, get_session, permission_check, db_event_commit
from .common_api import common_fields

get_parse = reqparse.RequestParser()
get_parse.add_argument('all', type=int)
get_parse.add_argument('id', type=int)

parse_base = reqparse.RequestParser()
parse_base.add_argument('action', type=str, required=True, help='Please choose a method.')

parse_register = parse_base.copy()
parse_register.add_argument('password', type=str, required=True, help='Password is required.')
parse_register.add_argument('phone', type=str, required=True, help="Phone is a must.")
parse_register.add_argument('name', type=str, required=True, help="Name is a must while register.")
parse_register.add_argument('address', type=str, required=True, help="Address is a must while register.")
parse_register.add_argument('gender', type=str, required=True, help="Gender is a must while register.")
parse_register.add_argument('email', type=str)

parse_login = parse_base.copy()
# 登陆方式存储在ApiConstant中
parse_login.add_argument('ident_by', type=int)
parse_login.add_argument('ident_data', type=str, required=True)
parse_login.add_argument('password', type=str, required=True, help='Password is required.')

parse_patch = parse_base.copy()
parse_patch.add_argument('old_password', type=str)
parse_patch.add_argument('new_password', type=str)
parse_patch.add_argument('id', type=int)
parse_patch.add_argument('phone', type=str)
parse_patch.add_argument('name', type=str)
parse_patch.add_argument('address', type=str)
parse_patch.add_argument('gender', type=str)
parse_patch.add_argument('email', type=str)

parse_delete = parse_base.copy()
parse_delete.add_argument('ident_by', type=int, required=True)
parse_delete.add_argument('ident_data', type=str, required=True)

parse_token = reqparse.RequestParser()
parse_token.add_argument('token', type=str, required=True)

parse_grant = reqparse.RequestParser()
parse_grant.add_argument('id', type=int, required=True)
parse_grant.add_argument('grant_code', type=int, required=True)


user_detail_fields = {
    'name': fields.String,
    'phone': fields.String,
    'email': fields.String,
    'gender': fields.String,
    'address': fields.String
}

user_query_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'data': fields.Nested(user_detail_fields)
}

users_query_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'data': fields.List(fields.Nested(user_detail_fields))
}

user_login_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'id': fields.Integer,
    'token': fields.String,
    'expires': fields.Integer
}

user_patch_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'password_change_status': fields.Integer,
    'new_data': fields.Nested(user_detail_fields)
}


class PreRegisterResource(Resource):
    """
        `Class is used for the pre-checking of the username and phone, email.`

    """
    pass


class UserResource(Resource):

    @staticmethod
    @login_required(TokenPrefix.BOTH)
    def get():
        args_get = get_parse.parse_args()
        _all = args_get.get('all')
        _id = args_get.get('id')

        if _id is not None:
            try:
                _id = int(_id)
                if not g.user.is_super:
                    # 非超级管理员不能查看不是自己的信息
                    if _id != g.user.id:
                        abort(ApiConstant.HTTP_FAILED, msg='Id Not Match.')
                else:
                    session = get_session()
                    user = session.query(User).get(_id)
                    # 如果没有找到用户
                    if user is None:
                        return marshal({'msg': 'Failed', 'status': ApiConstant.HTTP_FAILED}, user_query_fields)

                    # 如果用户被找到
                    sub_data = {
                        'name': user.name,
                        'phone': user.phone,
                        'email': user.e_mail,
                        'gender': user.gender,
                        'address': user.address
                    }
                    data = {
                        'msg': 'Success',
                        'status': ApiConstant.HTTP_OK,
                        'data': sub_data
                    }

                    return marshal(data, user_query_fields)

            except ValueError:
                pass

        # 进入ALL 逻辑
        if _all == '0':
            return marshal({'msg': 'Failed', 'status': ApiConstant.HTTP_FAILED}, users_query_fields)
        if not g.user.is_super:
            abort(ApiConstant.HTTP_FAILED, msg='Not Enough to Access.')
        session = get_session()
        users = session.query(User)
        # 准备数据
        ul = list()
        for user in users:
            sub_data = {
                'name': user.name,
                'phone': user.phone,
                'email': user.e_mail,
                'gender': user.gender,
                'address': user.address
            }
            ul.append(sub_data)

        data = {
            'msg': 'Success',
            'status': ApiConstant.HTTP_OK,
            'data': ul
        }

        return marshal(data, users_query_fields)

    @staticmethod
    def post():
        args = parse_base.parse_args()
        action = args.get('action', '').lower()

        if action == ApiConstant.USER_REGISTER:
            args_register = parse_register.parse_args()
            phone = args_register.get('phone')
            """
                There should be at least one prerequisite check, 
                but it's better when written in a new api class than here.
                
                !!! We treat this params as checked.
            """
            email = args_register.get('email')
            name = args_register.get('name')
            # 重复检测
            address = args_register.get('address')
            gender = args_register.get('gender')
            password = args_register.get('password')
            user = User(
                gender=gender,
                e_mail=email,
                name=name,
                address=address,
                phone=phone
            )
            user.password = password

            if user.save():
                data = {
                    'msg': 'Success',
                    'status': ApiConstant.HTTP_CREATE_OK
                }
            else:
                data = {
                    'msg': 'Failed',
                    'status': ApiConstant.HTTP_FAILED
                }

            return marshal(data, common_fields)

        elif action == ApiConstant.USER_LOGIN:
            # TODO 防止用户恶意登陆刷redis内存
            args_login = parse_login.parse_args()
            ident_by = args_login.get('ident_by')
            ident_data = args_login.get('ident_data')
            password = args_login.get('password')
            if ident_by:
                if ident_by == ApiConstant.IDENT_NAME:
                    user = get_user_by_name(ident_data)
                elif ident_by == ApiConstant.IDENT_EMAIL:
                    user = get_user_by_email(ident_data)
                elif ident_by == ApiConstant.IDENT_PHONE:
                    user = get_user_by_phone(ident_data)
                else:
                    abort(400, msg='Invalid ident_by.')
                    user = None
            else:
                user = get_user_by_raw_input(ident_data)

            if not user:
                abort(ApiConstant.LOGIN_FAILED, msg='Login Failed.')
            if not user.check_password(password):
                abort(ApiConstant.LOGIN_FAILED, msg='Login Failed.')
            if user.is_delete:
                abort(ApiConstant.LOGIN_FAILED_DELETED, msg='User not Exist.')

            # 使用is_super字段判断用户是否为超级管理员
            token = generate_token(TokenPrefix.NORMAL_USER if not user.is_super else TokenPrefix.ADMIN_USER)
            # 创建token并加入到redis中
            cache.set(token, user.id, timeout=ApiConstant.TOKEN_TIMEOUT)
            # TODO 正负映射的实现

            data = {
                'msg': 'Login Success',
                'status': ApiConstant.HTTP_OK,
                'id': user.id,
                'token': token,
                'expires': ApiConstant.TOKEN_TIMEOUT
            }

            return marshal(data, user_login_feedback_fields)

        elif action == ApiConstant.USER_PATCH:
            raw_data = UserResource.patch_()
            return marshal(raw_data, user_patch_feedback_fields)

        elif action == ApiConstant.USER_DELETE:
            args_delete = parse_delete.parse_args()
            idb = args_delete.get('ident_by')
            idd = args_delete.get('ident_data')

            raw_data = UserResource.delete_(idb, idd)
            data = {
                'msg': 'Success' if raw_data else 'Failed',
                'status': ApiConstant.HTTP_OK if raw_data else ApiConstant.HTTP_FAILED,
            }

            return marshal(data, common_fields)

        elif action == ApiConstant.USER_LOGOUT:
            args_token = parse_token.parse_args()
            token = args_token.get('token')
            if token is None:
                abort(ApiConstant.LOGIN_FAILED, msg='Invalid token.')
            else:
                res = cache.delete(key=token)
                print(res)
                data = {
                    'msg': 'Success',
                    'status': ApiConstant.HTTP_OK
                }
                return marshal(data, common_fields)

        elif action == ApiConstant.USER_GRANT:
            args_grant = parse_grant.parse_args()
            _id = args_grant.get('id')
            grant_code = args_grant.get('grant_code')
            raw_data = UserResource.grant(_id, grant_code)

            data = {
                'msg': 'Success' if raw_data else 'Failed',
                'status': ApiConstant.HTTP_OK if raw_data else ApiConstant.HTTP_FAILED,
            }

            return marshal(data, common_fields)

        else:
            abort(400, msg="Invalid Request.")

    @staticmethod
    @login_required(TokenPrefix.BOTH)
    def patch_() -> dict:

        new_data = {}

        args_patch = parse_patch.parse_args()
        # 修改密码逻辑
        old_password = args_patch.get('old_password')
        new_password = args_patch.get('new_password')
        _id = args_patch.get('id')
        session = get_session()

        # 获取用户
        user = session.query(User).get(_id) if _id is not None else None
        if user is None:
            user = g.user

        # 修改其他信息
        name = args_patch.get('name')
        phone = args_patch.get('phone')
        email = args_patch.get('email')
        address = args_patch.get('address')
        gender = args_patch.get('gender')

        user.name = name if name is not None and len(name) > 0 else user.name
        db_res = db_event_commit(session)
        if db_res:
            new_data.setdefault('name', name)

        user.phone = phone if phone is not None and len(phone) > 0 else user.phone
        db_res = db_event_commit(session)
        if db_res:
            new_data.setdefault('phone', phone)

        user.e_mail = email if email is not None and len(email) > 0 else user.e_mail
        db_res = db_event_commit(session)
        if db_res:
            new_data.setdefault('email', email)

        user.address = address if address is not None and len(address) > 0 else user.address
        db_res = db_event_commit(session)
        if db_res:
            new_data.setdefault('address', address)

        user.gender = gender if gender is not None and len(gender) > 0 else user.gender
        db_res = db_event_commit(session)
        if db_res:
            new_data.setdefault('gender', gender)

        feedback_data = {
            'msg': 'Success',
            'status': ApiConstant.HTTP_OK,
            'password_change_status': 0,
            'new_data': new_data
        }

        # 如果要修改密码
        if new_password is not None:
            if (_id is not None or name is not None) and user.is_super:
                # 意味着可以给任何用户修改密码
                if name is not None:
                    _user = session.query(User).filter_by(name=name).first()
                else:
                    _user = session.query(User).get(_id)

                if _user is None:
                    abort(400, msg='User not found.')
                pwd_change = not _user.check_password(new_password)
                if pwd_change:
                    _user.password = new_password
                    db_res = db_event_commit(session)

            elif old_password is not None and len(old_password) > 0 and user.check_password(old_password):
                # 更改密码完成
                pwd_change = not user.check_password(new_password)
                if pwd_change:
                    user.password = new_password
                    db_res = db_event_commit(session)
            else:
                pwd_change = False
            feedback_data['password_change_status'] = 1 if db_res and pwd_change else 0
        else:
            feedback_data['password_change_status'] = 0

        return feedback_data

    @staticmethod
    @permission_check('USER_INFO_DEL', TokenPrefix.ADMIN_USER)
    def delete_(idb: int, idd: str) -> bool:
        session = get_session()
        if idb == ApiConstant.IDENT_NAME:
            user = get_user_by_name(idd)
        elif idb == ApiConstant.IDENT_PHONE:
            user = get_user_by_phone(idd)
        elif idb == ApiConstant.IDENT_EMAIL:
            user = get_user_by_email(idd)
        else:
            abort(ApiConstant.HTTP_FAILED, msg='Invalid idb.')
            return False
        if user is not None:
            user.is_delete = True
        else:
            return False
        return db_event_commit(session)

    @staticmethod
    @permission_check('SUPER_ADMIN', TokenPrefix.ADMIN_USER)
    def grant(uid: int, grant_val: int) -> bool:
        if uid is None:
            abort(ApiConstant.HTTP_FAILED, msg='Invalid user id.')
            return False
        if grant_val is None:
            abort(ApiConstant.HTTP_FAILED, msg='Vague permission code.')
            return False

        session = get_session()
        user = session.query(User).get(uid)
        if user is None:
            abort(ApiConstant.HTTP_FAILED, msg='Invalid user id.')

        user.permission = grant_val
        return db_event_commit(session=session)
