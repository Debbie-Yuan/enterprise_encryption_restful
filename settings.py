from os.path import dirname, join, abspath


BASE_DIR = dirname(abspath(__file__))
PORTRAIT_DIR = join(join(join(BASE_DIR, 'static'), 'upload'), 'portrait')
TMP_DIR = join(join(join(BASE_DIR, 'static'), 'upload'), 'tmp')
NGINX_STATIC_PORTRAIT_URL = 'https://debbiee.cn/flask-static/'
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TokenPrefix:
    __slots__ = []

    BOTH = 'both'
    ADMIN_USER = 'admin'
    NORMAL_USER = 'normal'
    FACE_RECOGNITION_SESSION = 'frc'
    PORTRAIT_COLLECT = 'prtclt'


class ApiConstant:
    __slots__ = []

    HTTP_OK = 200
    HTTP_CREATE_OK = 201
    HTTP_CREATE_FAILED = 202
    LOGIN_FAILED = 305
    LOGIN_FAILED_DELETED = 306
    HTTP_FAILED = 400

    USER_LOGIN = 'login'
    USER_LOGOUT = 'logout'
    USER_REGISTER = 'register'
    USER_PATCH = 'patch'
    USER_GRANT = 'grant'
    USER_DELETE = 'delete'
    ATT_DEL = 'att_del'
    ATT_ADD = 'att_add'
    PRT_AUTH = 'prt_auth'
    PRT_GET = 'prt_get'

    IDENT_NAME = 11
    IDENT_EMAIL = 12
    IDENT_PHONE = 13
    ATT_ADD_SUP = 14
    ATT_ADD_FRC = 15
    ATT_ADD_TRA = 16

    PRT_TOKEN_TIMEOUT = 60 * 2
    TOKEN_TIMEOUT = 60 * 10


def concat_database_url(info: dict):
    db = info.get('db')
    driver = info.get('driver')
    user = info.get('user')
    pwd = info.get('pwd')
    host = info.get('host')
    port = info.get('port')
    db_name = info.get('name')

    return '{}+{}://{}:{}@{}:{}/{}'.format(
        db, driver, user, pwd, host, port, db_name
    )


class Config:
    __slots__ = []

    DEBUG = False
    SETING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'mb4sux/;ais92ls82@9'
    MAX_CONTENT_LENGTH = 1024 * 1024


class DevelopConfig(Config):
    __slots__ = []

    DEBUG = True
    _info = {
        'db': 'mysql',
        'driver': 'pymysql',
        'user': 'root',
        'pwd': '981209',
        'host': 'localhost',
        'port': 3306,
        'name': 'enterprise_encryption',
    }

    SQLALCHEMY_DATABASE_URI = concat_database_url(_info)


envs = {
    'develop': DevelopConfig,
    'default': DevelopConfig,
}
