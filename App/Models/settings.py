from typing import Callable


class Permission:

    SUPER_ADMIN = 65536

    USER_INFO_QUERY = 1
    USER_INFO_DEL = 2
    USER_INFO_PATCH = 4
    USER_INFO_ADD = 8

    ATTENDANCE_QUERY_BY_ROLE = 16
    ATTENDANCE_QUERY_ALL = 32

    ATTENDANCE_DEL = 64
    ATTENDANCE_ADD = 128
    # 系统的默认设计是不可更改签到记录

    PORTRAIT_ADD = 256
    PORTRAIT_DEL = 512
    PORTRAIT_QUERY = 1024

    LOG_QUERY_BY_USER = 2048
    LOG_QUERY_ALL = 4096

    # 普通用户权限中包括了
    #   用户信息查询
    #   用户信息修改
    #   用户签到按用户id查询
    #   用户签到添加
    #   用户肖像添加
    #   用户肖像查询
    #   用户日志按用户id查询
    @staticmethod
    def grant_normal_code():
        return Permission.USER_INFO_QUERY + Permission.USER_INFO_PATCH + \
               Permission.ATTENDANCE_QUERY_BY_ROLE + Permission.ATTENDANCE_ADD + Permission.PORTRAIT_ADD + \
               Permission.PORTRAIT_QUERY + Permission.LOG_QUERY_BY_USER

    # 超级管理员中拥有所有权限
    @staticmethod
    def grant_super_code():
        return sum(
            (getattr(Permission, attr) for attr in dir(Permission) if not attr.startswith('__')
             and not isinstance(getattr(Permission, attr), Callable))
        )
