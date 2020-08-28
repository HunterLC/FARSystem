import collections
import math
import os
import datetime
import requests
from flask import Blueprint, jsonify, redirect, url_for, session
from flask import request
from flask import render_template
from sqlalchemy import func, and_
from .. import db
from ..models import Users
import pandas as pd
import numpy as np

setting_blue = Blueprint('setting', __name__)


@setting_blue.route('/', methods=['GET', 'POST'])
def start():
    user_list = db.session.query(Users).filter(Users.user_id == session['userid']).all()[0]
    db.session.close()
    return render_template('setting.html', User=user_list)


@setting_blue.route('/updateUser', methods=['GET', 'POST'])
def update_user():
    if request.method == "POST":
        print(request.form)
        user_name = request.form.get('user_name')
        user_gender = request.form.get('user_gender')
        user_desc = request.form.get('user_desc')
        user_old_pass = request.form.get('user_old_pass')
        user_new_pass = request.form.get('user_new_pass')
        if user_old_pass != '' and user_new_pass != '':
            # 包括修改密码
            if Users.query.filter_by(user_id=session['userid']).update({'user_name': user_name,
                                                                        'user_gender': user_gender,
                                                                        'user_desc': user_desc,
                                                                        'user_password': user_new_pass}) == 1:
                db.session.commit()
            else:
                return {'result': 0}
        else:
            # 不包括修改密码
            if Users.query.filter_by(user_id=session['userid']).update({'user_name': user_name,
                                                                        'user_gender': user_gender,
                                                                        'user_desc': user_desc}) == 1:
                db.session.commit()
            else:
                return {'result': 0}
        session['username'] = user_name
        session['usergender'] = user_gender
        session['userdesc'] = user_desc
        return {'result': 1}
