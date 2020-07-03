from flask import Flask

from App.ext import init_ext
from settings import envs
from App.Apis import init_apis


def init_app(env):
    # 获取flask实例
    app = Flask(__name__)
    # 从配置文件中加载配置
    app.config.from_object(envs.get(env))
    # 加载扩展库
    init_ext(app)
    # 初始化API接口
    init_apis(app)

    return app
