from flask import Blueprint, redirect, url_for
from flask import request
from flask import render_template
from flask import session
from sqlalchemy import and_

from .. import db
from app.models import Actors, Users, Likes

account_blue = Blueprint('account', __name__)


@account_blue.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html", errors="")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter(and_(username == Users.user_email, password == Users.user_password)).all()
        if len(user) > 0:
            session['username'] = user[0].user_name
            session['userimage'] = user[0].user_image
            session['userid'] = user[0].user_id
            session['useremail'] = user[0].user_email
            session['usergender'] = user[0].user_gender
            session['userdesc'] = user[0].user_desc
            session['isLogin'] = True
            return redirect(url_for('actor.start'), code=302)
        else:
            return render_template("login.html", errors="密码错误")

@account_blue.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == "GET":
        session.clear()
        return redirect(url_for('login'), code=302)

@account_blue.route('/forget', methods=['GET', 'POST'])
def forget():
    return render_template("forgot-password.html")


@account_blue.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("register.html",username="", email="", password="",re_password="", error='')


@account_blue.route('/checkRegister', methods=['GET', 'POST'])
def user_register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        re_password = request.form.get('re_password')
        if check_email_valid(email=email)['valid'] != 1:
            return render_template("register.html", username=username, email=email, password=password,
                                   re_password=re_password, error='邮箱已经被注册！')
        elif password != re_password:
            return render_template("register.html", username=username, email=email, password="",
                                   re_password="", error='密码输入不一致！')
        else:
            # 注册成功
            # 插入用户信息
            user = Users(username,email,password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'), code=302)


@account_blue.route('/checkEmailValid', methods=['GET', 'POST'])
def check_email_valid(email=""):
    if request.method == "GET":
        email = request.args.get('email')
    valid = 1
    user_list = db.session.query(Users).filter(Users.user_email == email).all()
    db.session.close()
    if len(user_list) > 0:
        # 查找到相同的邮箱，说明该邮箱已经被注册过，则该邮箱不合法
        valid = 0
    response = {'valid': valid}
    return response

@account_blue.route('/likeActor', methods=['GET', 'POST'])
def like_actors():
    if request.method == "GET":
        actor_id = request.args.get('actor_id').replace('likeButton','')
        user_id = session['userid']
        result = Likes.query.filter(and_(actor_id == Likes.actor_id, user_id == Likes.user_id)).all()
        db.session.close()
        response = {}
        if len(result) > 0:
            # 该演员目前为喜欢状态，再次点击即代表取消操作，执行delete
            db.session.query(Likes).filter(and_(actor_id == Likes.actor_id, user_id == Likes.user_id)).delete()
            db.session.commit()
            response['type'] = 'unlike'
        elif len(result) == 0:
            # 该演员目前为不喜欢状态，再次点击即代表新增操作，执行add
            like = Likes(user_id, actor_id)
            db.session.add(like)
            db.session.commit()
            response['type'] = 'like'
        return response


