import os

import requests
from flask import Blueprint
from flask import request
from flask import render_template
from .. import db
from ..models import Actors, Awards, Films

film_blue = Blueprint('film', __name__)


@film_blue.route('/', methods=['POST', 'GET'])
def start(page=20):
    if request.method == 'GET':
        # 前端传过来的id格式中含有前缀moreButton
        if request.args.get('page'):
            page = int(request.args.get('page'))
        print(page)
        paginate_films = get_all_films(page=page)
        return render_template('film.html', Films=paginate_films)

def get_all_films(page=1, pre_page=30):
    paginate_films = Films.query.paginate(page, pre_page)
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
                name = film.film_protagonist.encode('utf-8').decode("utf-8")[0:80]+"..."
            film.film_protagonist = name
        return films
