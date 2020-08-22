import os

import requests
from flask import Blueprint, session
from flask import request
from flask import render_template
from .. import db
from ..models import Actors, Awards, Films
from sqlalchemy import or_, and_, text

film_blue = Blueprint('film', __name__)


@film_blue.route('/', methods=['POST', 'GET'])
def start(page=1, value="film_year"):
    if request.method == 'GET':
        if not request.args.get('page') and not request.args.get('film_type') and not request.args.get(
                'film_year') and not request.args.get('search') and not request.args.get('sorted_by'):
            paginate_films = get_all_films(page=page)
            return render_template('film.html', Films=paginate_films,value=value, Session=session)
        else:
            # 前端传过来的id格式中含有前缀moreButton
            if request.args.get('page'):
                page = int(request.args.get('page'))
            print(page)
            if request.args.get('film_type'):
                film_type = request.args.get('film_type').rstrip()
                print(request.args.get('film_type').rstrip())
            else:
                film_type = ""
            if request.args.get('film_year') and request.args.get('film_year') != "":
                film_year = int(request.args.get('film_year'))
                print(request.args.get('film_year'))
            else:
                film_year = ""
            if request.args.get('search'):
                search = request.args.get('search')
                print(request.args.get('search'))
            else:
                search = ""
            if request.args.get('sorted_by'):
                value = request.args.get('sorted_by')
                print(request.args.get('sorted_by'))
            else:
                value = "film_year"
            paginate_films = get_all_films(page=page, film_year=film_year, film_type=film_type, search=search, value=value)
            return render_template('film.html', film_type=film_type, film_year=film_year, search=search,
                                   Films=paginate_films, value=value, Session=session)


def get_all_films(page=1, pre_page=30, film_year=0, film_type="", search="", value="film_year"):
    if film_year != 0 and film_year != "":
        paginate_films = Films.query.filter(
            and_(Films.film_type.like('%' + film_type + '%'), Films.film_year == film_year,
                 or_(Films.film_name.like('%' + search + '%'),
                     Films.film_protagonist.like('%' + search + '%')))).order_by(text("-"+value)).paginate(page,
                                                                                 pre_page)
    else:
        paginate_films = Films.query.filter(
            and_(Films.film_type.like('%' + film_type + '%'),
                 or_(Films.film_name.like('%' + search + '%'),
                     Films.film_protagonist.like('%' + search + '%')))).order_by(text("-"+value)).paginate(page,
                                                                                 pre_page)
    db.session.close()
    for film in paginate_films.items:
        film.film_img = film.film_img.split('/')[-1]
        name = film.film_protagonist.encode('utf-8').decode("utf-8")
        if len(name) > 80:
            name = film.film_protagonist.encode('utf-8').decode("utf-8")[0:80] + "..."
        film.film_protagonist = name
    return paginate_films


@film_blue.route('/downloadFilmImg', methods=['POST', 'GET'])
def download_film_img():
    films = db.session.query(Films).all()
    db.session.close()
    for film in films:
        img_name = film.film_img.split('/')[-1]
        img_path = r'E:\PythonCode\FARSystem\static\image\film\{}'.format(img_name)
        print(img_path)
        try:
            if not os.path.exists(img_path):
                r = requests.get(film.film_img)
                with open(img_path, 'wb') as f:
                    f.write(r.content)
                    f.close()
                    print("文件保存成功")
            else:
                print("文件已存在")
        except Exception as err:
            print(err)
    return 'success'


def get_films_by_actor_id():
    if request.method == 'GET':
        # 前端传过来的id格式中含有前缀moreButton
        if request.args.get('actor_id'):
            actor_id = request.args.get('actor_id').replace('moreButton', '')
        else:
            actor_id = 1314124
        # 根据演员的id去查询演员的电影信息
        films = Films.query.filter_by(actor_id=actor_id).all()
        db.session.close()
        for film in films:
            film.film_img = film.film_img.split('/')[-1]
            name = film.film_protagonist.encode('utf-8').decode("utf-8")
            if len(name) > 80:
                name = film.film_protagonist.encode('utf-8').decode("utf-8")[0:80] + "..."
            film.film_protagonist = name
        return films


@film_blue.route('/getFilmInfo', methods=['POST', 'GET'])
def get_film_info():
    if request.method == 'GET':
        # 前端传过来的id格式中含有前缀moreButton
        film_id = request.args.get('film_id').replace('moreFilmButton', '')
        # 根据演员的id去查询演员的基本信息
        film_info = Films.query.filter_by(film_id=film_id).all()[0]
        db.session.close()
        film_info.film_img =  film_info.film_img.split('/')[-1]
        return render_template('filminfo.html',Film=film_info, Session=session)