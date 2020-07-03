from typing import Callable

from flask import request, g
from flask_restful import abort
from App.ext import cache, get_session
from settings import TokenPrefix, TIME_FORMAT
from App.Models.User import User
from datetime import datetime


def _verify(user_type: str):
    token = request.args.get('token') or request.form.get('token')
    if not token:
        abort(401, msg="Not Logged In.")
    # 验证超级管理员权限
    if user_type == TokenPrefix.ADMIN_USER and not token.startswith(TokenPrefix.ADMIN_USER):
        abort(401, msg="Use Normal Privilege As Admin.")
    # 验证普通用户权限
    if user_type == TokenPrefix.NORMAL_USER and not token.startswith(TokenPrefix.NORMAL_USER):
        abort(401, msg="Privilege Error.")
    # 如果两者都可以
    if user_type == TokenPrefix.BOTH:
        if not any(
                (token.startswith(getattr(TokenPrefix, prefix)) for prefix in dir(TokenPrefix)
                 if not prefix.startswith('__') and not isinstance(getattr(TokenPrefix, prefix), Callable))):
            abort(401, msg="Invalid token.")
    # 获取user id 根据token
    user_id = cache.get(token)
    if user_id is None:
        abort(401, msg="Invalid Token.")
    session = get_session()
    user_instance = session.query(User).get(user_id)
    if user_instance is None:
        abort(401, msg="Invalid ID")
    g.user = user_instance
    g.token = token


def login_required(user_type):
    def decorate(fun):
        def _login_check(*args, **kwargs):
            _verify(user_type)
            return fun(*args, **kwargs)
        return _login_check
    return decorate


def face_recognition_required(fun):
    def decorate(*args, **kwargs):
        # 获取面容token
        frc_token = request.args.get('frc_token')
        if frc_token is None:
            abort(403, msg='Forbidden')
            return
        user_id = cache.get(frc_token)
        if not frc_token.startswith(TokenPrefix.FACE_RECOGNITION_SESSION) or user_id is None:
            abort(401, msg='Invalid token.')
            return
        # 删除frc_token
        cache.delete(frc_token)
        # 获取用户实例
        session = get_session()
        user_instance = session.query(User).get(user_id)
        if user_instance is None:
            abort(401, msg="Invalid ID")
        g.user = user_instance

        # 执行被装饰逻辑
        return fun(*args, **kwargs)
    return decorate


def permission_check(permission, user_type):
    def decorate(fun):
        def _permission_check(*args, **kwargs):
            _verify(user_type)
            if not g.user.check_permission(permission):
                abort(403, msg="Not Enough Privilege")
            return fun(*args, **kwargs)
        return _permission_check
    return decorate


def get_user_by_raw_input(user_data: str or int) -> None or User:
    """

    :param user_data: Use user data rather than username because in real cases, user may login using his phone,
                      or email address. As for efficiency of the user interface, we don't suggest out user to
                      input specific data in specific area, you can enter your ident in just one place.
    :return: App.Models.User
    """
    if not user_data:
        return None

    session = get_session()
    # 用户名检测
    user = session.query(User).filter_by(name=user_data).first()
    if user is not None:
        return user

    # 用户id检测
    if isinstance(user_data, int):
        user = session.query(User).get(user_data)
        if user:
            return user

    # 检测用户手机号
    user = session.query(User).filter_by(phone=user_data).first()
    if user:
        return user

    # 检测用户邮箱
    user = session.query(User).filter_by(e_mail=user_data).first()
    if user:
        return user

    return None


def get_user_by_name(name: str) -> User or None:
    session = get_session()
    return session.query(User).filter_by(name=name).first()


def get_user_by_email(email: str) -> User or None:
    session = get_session()
    return session.query(User).filter_by(e_mail=email).first()


def get_user_by_phone(phone: str) -> User or None:
    session = get_session()
    return session.query(User).filter_by(phone=phone).first()


def db_event_commit(session, success_callback: Callable or None = None, failing_callback: Callable or None = None):
    try:
        session.commit()
        if success_callback is not None:
            success_callback()
        print(1)
        return True
    except Exception:
        session.rollback()
        print(0)
        if failing_callback is not None:
            failing_callback()
        return False


def datetime_to_str(dt: datetime):
    return dt.strftime(TIME_FORMAT)


def str_to_datetime(pat: str):
    return datetime.strptime(pat, TIME_FORMAT)
