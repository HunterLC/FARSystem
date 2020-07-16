from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # 实例化

from .models import *
from app.views.account import account_blue
from app.views.actor import actor_blue


def init_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config.from_object('settings.DevelopmentConfig')

    # 将db注册到app中
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(actor_blue, url_prefix='/actor')
    app.register_blueprint(account_blue, url_prefix='/account')

    return app
