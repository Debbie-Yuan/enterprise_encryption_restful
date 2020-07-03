from flask_restful import fields, marshal


common_fields = {
    'msg': fields.String,
    'status': fields.Integer,
}


def get_common_marshaled(msg=None, status=None):
    return marshal({'msg': msg, 'status': status}, common_fields)
