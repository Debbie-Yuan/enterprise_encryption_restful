from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_caching import Cache
from sqlalchemy.orm import Session


# 需要被调用的扩展控件
db = SQLAlchemy()
migrate = Migrate()
cache = Cache(
    config={
        'CACHE_TYPE': 'redis',
    }
)


def get_session() -> Session:
    return db.session


# 向app注册扩展库
def init_ext(app):
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    DebugToolbarExtension(app)
