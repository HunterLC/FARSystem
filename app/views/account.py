from flask import Blueprint, redirect, url_for
from flask import request
from flask import render_template
from flask import session
from .. import db
from app.models import Actors

account_blue = Blueprint('account', __name__)

@account_blue.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html", errors="")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin@qq.com' and password == '123456':
            session['username'] = username
            session['isLogin'] = True
            return redirect(url_for('actor.start'), code=302)

        else:
            return render_template("login.html", errors="密码错误")
        # user_obj=db.session.query(models.Actors).all()
        # print(user_obj[0].to_json())
        # db.session.close()
        # if user_obj:
        #     return '登陆成功'
        # else:
        #     return render_template("login.html", errors="用户名或密码错误！")


@account_blue.route('/forget', methods=['GET', 'POST'])
def forget():
    return render_template("forgot-password.html")


@account_blue.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("register.html")
