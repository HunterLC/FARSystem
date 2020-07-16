import math

from flask import Blueprint
from flask import request
from flask import render_template
from .. import db
from ..models import Actors, Awards, Films


actor_blue = Blueprint('actor', __name__)


@actor_blue.route('/')
def hello_world():
    return 'Hello World! actor'


@actor_blue.route('/init-info')
def init_avg_info():
    """
    初始化演员的平均电影评分和平均电影评分人数
    :return:
    """
    actor_info = Actors.query.all()
    print(actor_info[0].actor_id)
    for actor in actor_info:
        # 获取演员的id
        actor_id = actor.actor_id
        # 根据演员的id去查询演员的电影
        film_info = Films.query.filter_by(actor_id=actor_id).all()
        if film_info:
            # 电影总分数
            film_all_score = 0
            # 电影总评论数
            film_all_comments = 0
            for film in film_info:
                film_all_score += film.film_score
                film_all_comments += film.film_comments_sum
            avg_film_all_score = film_all_score / len(film_info)
            # 电影平均评论人数向下取整
            avg_film_all_comments = math.floor(film_all_comments / len(film_info))
            print('{}的平均电影评分{}，平均电影评分人数{}'.format(actor.actor_c_name, avg_film_all_score, avg_film_all_comments))
            # 更新表
            if Actors.query.filter_by(actor_id=actor_id).update({'actor_avg_films_score': avg_film_all_score, 'actor_avg_comments_sum':avg_film_all_comments}) == 1:
                db.session.commit()
            else:
                print('更新{}信息出错'.format(actor.actor_c_name))
        else:
            print('没有查询到{}的电影信息'.format(actor.actor_c_name))
    db.session.close()
    return '演员的平均电影评分和平均电影评分人数成功计算并更新到数据库中'
