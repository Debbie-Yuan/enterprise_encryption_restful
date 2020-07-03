from flask import g
from flask_restful import Resource, reqparse, fields, marshal, abort

from App.Apis.User.common_api import get_common_marshaled
from App.Apis.api_utils import login_required, permission_check, db_event_commit, face_recognition_required
from settings import ApiConstant, TokenPrefix
from App.ext import get_session
from App.Models.User import Attendance, User
from App.Apis.api_utils import datetime_to_str
from datetime import datetime as dt

base_att_fields = {
    'uid': fields.Integer,
    'username': fields.String,
    'att_datetime': fields.String,
    'gender': fields.String,
}

single_att_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'data': fields.Nested(base_att_fields)
}


user_att_nested_fields = {
    'uid': fields.Integer,
    'gender': fields.String,
    'username': fields.String,
    'data': fields.List(fields.String)
}


multi_att_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'data': fields.Nested(user_att_nested_fields)
}


multi_att_users_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'data': fields.List(fields.Nested(user_att_nested_fields))

}


def init_single_user_dict(uid, username, gender=None) -> dict:
    return {
        'uid': uid,
        'username': username,
        'gender': gender,
        'data': list()
    }


base_parse = reqparse.RequestParser()
base_parse.add_argument('action', type=str, required=True, help='Specify the access method.')
base_parse.add_argument('method', type=int, required=True, help='Specify the logic method symbol.')
base_parse.add_argument('uid', type=int)

get_parse = reqparse.RequestParser()
get_parse.add_argument('start', type=str)
get_parse.add_argument('end', type=str)
get_parse.add_argument('all', type=int)
get_parse.add_argument('id', type=int)


class UserAttendanceResource(Resource):

    @staticmethod
    @login_required(TokenPrefix.BOTH)
    def get():
        if g.user is None:
            abort(401, msg='Please login.')
        current_user = g.user
        assert isinstance(current_user, User)
        current_user_id = g.user.id

        args_get = get_parse.parse_args()
        # TODO 增加限定时间范围的查询
        # start = args_get.get('start')
        # end = args_get.get('end')
        _all = args_get.get('all')
        _id = args_get.get('id')

        if _id is not None:
            # 判断用户id与给定id是否相等
            if current_user_id != _id:
                if not current_user.is_super and not current_user.check_permission('ATTENDANCE_QUERY_ALL'):
                    abort(403, msg='Forbidden')
                    return None
                # 当前用户是超级管理员或有权限查看全部
                # 可以查询当前给定id的内容
            session = get_session()
            results = session.query(User.id, User.name, User.gender, Attendance.check_datetime) \
                .join(User, Attendance.staff_id == User.id).filter_by(id=_id)

            feedback_list = list()
            result = None

            for result in results:
                feedback_list.append(datetime_to_str(result.check_datetime))

            feedback_data = {
                'msg': 'Success',
                'status': ApiConstant.HTTP_OK,
                'data': {
                    'uid': result.id,
                    'gender': result.gender,
                    'username': result.name,
                    'data': feedback_list
                }
            }
            return marshal(feedback_data, multi_att_feedback_fields)

        elif _all is not None and _all == 1:
            if current_user.is_super or current_user.check_permission('ATTENDANCE_QUERY_ALL'):
                # 给返回全部数据
                uid_set = set()
                session = get_session()
                results = session.query(User.id, User.name, User.gender, Attendance.check_datetime). \
                    join(User, Attendance.staff_id == User.id)
                feedback_dict = dict()

                # for result in results:
                #     print(type(result))
                #     print(result)
                #     print(str(list(k for k in dir(result) if not k.startswith('__'))))
                #
                """
                    (2, 'steven', datetime.datetime(2020, 7, 2, 10, 52, 33))
                    ['check_datetime', 'count', 'id', 'index', 'keys', 'name']
                    如上连接查询会返回上面的结果，只需要使用result.name, result.id, result.check_datetime即可使用
                """

                for result in results:
                    if result.id not in uid_set:
                        # 如果不在，则加入用户id
                        uid_set.add(result.id)
                        feedback_dict.setdefault(result.id, init_single_user_dict(result.id,
                                                                                  result.name,
                                                                                  result.gender))
                    # 执行添加逻辑
                    feedback_dict.get(result.id).get('data').append(datetime_to_str(result.check_datetime))

                feedback_data = {
                    'msg': 'Success',
                    'status': ApiConstant.HTTP_OK,
                    'data': list(feedback_dict.values())
                }

                return marshal(feedback_data, multi_att_users_feedback_fields)
            else:
                abort(403, msg='Forbidden')

    @staticmethod
    def post():
        session = get_session()
        args_att = base_parse.parse_args()
        action = args_att.get('action')
        method = args_att.get('method')
        uid = args_att.get('uid')

        if action is None:
            abort(400, msg='Method not allowed.')

        if action == ApiConstant.ATT_ADD:
            if method == ApiConstant.ATT_ADD_SUP:
                att = UserAttendanceResource.add_manually(uid=uid)
            elif method == ApiConstant.ATT_ADD_FRC:
                att = UserAttendanceResource.add_automatically()
            elif method == ApiConstant.ATT_ADD_TRA:
                att = UserAttendanceResource.add_traditionally()
            else:
                abort(400, msg='Method not allowed.')
                return
            session.add(att)
            raw_data = db_event_commit(session)
            msg = 'Success' if raw_data else 'Failed'
            status = ApiConstant.HTTP_OK if raw_data else ApiConstant.HTTP_FAILED
            return get_common_marshaled(msg=msg, status=status)

        elif action == ApiConstant.ATT_DEL:
            # TODO  删除考勤记录接口
            pass
        else:
            abort(400, msg='Invalid Action.')

    @staticmethod
    @permission_check('SUPER_ADMIN', TokenPrefix.ADMIN_USER)
    def add_manually(uid: int) -> Attendance:
        return Attendance(staff_id=uid, check_datetime=dt.now())

    @staticmethod
    @face_recognition_required
    def add_automatically() -> Attendance or None:
        user = g.user
        if user is None:
            abort(500, msg='Internal Algorithm Error.')
            return None
        return Attendance(staff_id=user.id, check_datetime=dt.now())

    @staticmethod
    @login_required(TokenPrefix.BOTH)
    def add_traditionally() -> Attendance or None:
        user = g.user
        if user is None:
            abort(403, msg='No Privilege for Access.')
            return None
        return Attendance(staff_id=user.id, check_datetime=dt.now())
