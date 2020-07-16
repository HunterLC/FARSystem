from flask import Blueprint
from flask import request
from flask import render_template
from .. import db
from .. import models

account_blue = Blueprint('account', __name__)

@account_blue.route('/')
def hello_world():
    return 'Hello World! account'

@account_blue.route('/login',methods=['GET','POST'])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        return render_template("login.html", errors="用户名或密码错误！")
        # user_obj=db.session.query(models.Actors).all()
        # print(user_obj[0].to_json())
        # db.session.close()
        # if user_obj:
        #     return '登陆成功'
        # else:
        #     return render_template("login.html", errors="用户名或密码错误！")