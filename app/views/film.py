import os

import requests
from flask import Blueprint
from flask import request
from flask import render_template
from .. import db
from ..models import Actors, Awards, Films

film_blue = Blueprint('film', __name__)


@film_blue.route('/')
def hello_world():
    return 'Hello World! film'


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
