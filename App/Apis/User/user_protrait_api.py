from os.path import join
from urllib.parse import urljoin

from flask import request, g
from flask_restful import Resource, reqparse, fields, marshal, abort

from App.Apis.api_utils import login_required, db_event_commit
from App.utils import generate_token
from settings import ApiConstant, TokenPrefix, PORTRAIT_DIR, NGINX_STATIC_PORTRAIT_URL
from App.ext import get_session, cache
from App.Models.User import PortraitRecords, PortraitFileNames
from hashlib import md5
import time

import os


"""
    本API需要实现的功能：
        1。实现前端在登陆的情况下，对用户信息进行录入,字段要求为 ['POST']
            1. 要上传的用户id
            2. 当前操作人员token
            2-，当前的录入token
            3. 要上传的用户肖像帧，要求分辨率在100 * 235内，长宽比为1：2.35（标准电影格式），图片大小不高于128KB （
                                HTTP Header: Content-Length: < 128 * 1024）
            
            ``服务返回 ： 
                1. 上传是否成功 - HTTP Status
                2. 当前该用户的总肖像数
            
        2。普通用户获取自己的肖像，管理员用户获取任一用户肖像 ['GET']
            1. 要加载的用户id
            2. 当前操作人员token
            3. 长度限制 - 可选 - int
            4. 操作 ['action'] = content
            
            ``服务返回 ： 
                1. 上传是否成功 - HTTP Status
                2. 所有肖像的静态链接列表
        
        3。用户上传肖像前需要向服务器申请上传会话令牌 ['GET'] - action = auth
            1. 当前操作人员token
            2. 要上传肖像的总数amt
            3. 操作 ['action'] = auth
                
                ``服务返回 ：
                    1. 获取是否成功 - HTTP Status
                    2. 会话令牌 - 以portrait开头
"""

post_parse = reqparse.RequestParser()
post_parse.add_argument('id', type=int, required=True)
post_parse.add_argument('prt_token', type=str, required=True)

get_parse = reqparse.RequestParser()
get_parse.add_argument('action', type=str, required=True)

content_get_parse = get_parse.copy()
content_get_parse.add_argument('id', type=int, required=True)
content_get_parse.add_argument('length-limit', type=int)


auth_parse = get_parse.copy()
auth_parse.add_argument('amt')

post_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'portrait_amt': fields.Integer
}

get_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'data': fields.List(fields.String)
}

auth_feedback_fields = {
    'msg': fields.String,
    'status': fields.Integer,
    'token': fields.String
}


class UserPortraitResource(Resource):

    @staticmethod
    @login_required(TokenPrefix.BOTH)
    def get():
        args_get = get_parse.parse_args()
        action = args_get.get('action')
        if action is None:
            abort(500, msg='Bad request.')
            return
        if action == ApiConstant.PRT_AUTH:
            # 执行 收集令牌发放逻辑
            amt = auth_parse.parse_args().get('amt')
            if amt is None:
                abort(500, msg='Bad request.')
                return

            token = generate_token(TokenPrefix.PORTRAIT_COLLECT)
            cache.set(token, amt, timeout=ApiConstant.PRT_TOKEN_TIMEOUT)

            feedback = {
                'msg': 'Success',
                'status': ApiConstant.HTTP_OK,
                'token': token
            }
            return marshal(feedback, auth_feedback_fields)
        elif action == ApiConstant.PRT_GET:
            args_content = content_get_parse.parse_args()
            # 在使用argparser后，若不给参数，无法执行到此处
            _id = args_content.get('id')
            limit = args_content.get('length-limit')

            if not g.user.is_super and g.user.id != _id:
                abort(401, msg='You can\'t look up other\'s portrait.')

            # 执行 图片静态地址映射逻辑
            session = get_session()

            if limit is None:
                prf = session.query(PortraitFileNames).filter_by(staff_id=_id)
            elif limit <= 0:
                abort(403, msg='Invalid limit.')
                return
            else:
                prf = session.query(PortraitFileNames).filter_by(staff_id=_id).limit(limit)
            if prf is None:
                abort(404, msg='Not Found.')

            outer_url = urljoin(NGINX_STATIC_PORTRAIT_URL, str(_id))
            url_list = [join(outer_url, fn.staff_portrait_md5) for fn in prf]

            feedback = {
                'msg': 'Success',
                'status': ApiConstant.HTTP_OK,
                'data': url_list
            }
            return marshal(feedback, get_feedback_fields)
        else:
            abort(500, msg='Bad request.')

    @staticmethod
    @login_required(TokenPrefix.BOTH)
    def post():
        args_post = post_parse.parse_args()
        prt_token = args_post.get('prt_token')
        _id = args_post.get('id')

        if prt_token is None:
            abort(401, msg='No Prt Session Token.')
        if _id is None:
            abort(401, msg='Invalid id.')

        data = request.files.get('data')
        if data is None:
            abort(500, msg='No data uploaded or received.')
        # 使用时间戳和id的方式对文件命名
        fn = str(time.time()) + str(_id)
        fn = md5(fn.encode('utf-8')).hexdigest()

        prefix = os.path.join(PORTRAIT_DIR, str(_id))
        if not os.path.exists(prefix):
            os.mkdir(prefix)

        pr = PortraitRecords(staff_id=_id, staff_portrait_prefix=prefix)
        pfn = PortraitFileNames(staff_id=_id, staff_portrait_md5=fn)

        session = get_session()
        session.add(pr)
        session.add(pfn)
        db_feedback = db_event_commit(session)
        f_abs_name = os.path.join(prefix, fn)
        data.save(f_abs_name)

        # 检测文件是否存在
        save_feedback = os.path.exists(f_abs_name)

        return marshal({
                'msg': 'Success' if save_feedback and db_feedback else 'Failed',
                'status': ApiConstant.HTTP_OK if save_feedback and db_feedback else ApiConstant.HTTP_FAILED
                # TODO get portrait amount.
            },
            post_feedback_fields
        )

        # 以下为文件内容提取部分
        # assert isinstance(data, werkzeug.datastructures.FileStorage)
        # print(type(data.stream), data.stream)
        # dt = data.stream
        # assert isinstance(dt, tempfile.SpooledTemporaryFile)
        # print(dt.read())
        # print('data')
