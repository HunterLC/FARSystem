import collections
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
            if Actors.query.filter_by(actor_id=actor_id).update({'actor_avg_films_score': avg_film_all_score,
                                                                 'actor_avg_comments_sum': avg_film_all_comments}) == 1:
                db.session.commit()
            else:
                print('更新{}信息出错'.format(actor.actor_c_name))
        else:
            print('没有查询到{}的电影信息'.format(actor.actor_c_name))
    db.session.close()
    return '演员的平均电影评分和平均电影评分人数成功计算并更新到数据库中'


@actor_blue.route('/getFilmTypeDistribution', methods=['POST', 'GET'])
def get_film_type_distribution(time=0):
    """
    获取演员出演电影的类型分布
    :return:
    """
    if request.method == 'GET':
        actor_id = request.args.get('actor_id')
        # 根据演员的id去查询演员的电影
        if time != 0:
            film_info = Films.query.filter_by(actor_id=actor_id, film_year=time).all()
        else:
            film_info = Films.query.filter_by(actor_id=actor_id).all()
        db.session.close()
        if film_info:
            # 记录电影的类型列表
            film_type_list = []
            for film in film_info:
                if film.film_type == '':
                    film_type_list.append('无')
                else:
                    film_type_info = film.film_type.split(' ')
                    film_type_list.extend(film_type_info[0:-2])
            # 元素计数
            film_type_dict = dict(collections.Counter(film_type_list))
            final_dict = {}
            i = 0
            for k, v in film_type_dict.items():
                type_dict = {'type': k, 'count': v}
                final_dict[i] = type_dict
                i += 1
            """
            for example {0: {'region': '中国大陆', 'count': 50}, 1: {'region': '中国香港', 'count': 1}, 2: {'region': '中国台湾', 'count': 1}, 3: {'region': '中国', 'count': 1}, 4: {'region': '无', 'count': 5}}

            """
            print(final_dict)
            return final_dict
        else:
            return '没有查询到电影的类型信息'


@actor_blue.route('/getFilmRegionDistribution', methods=['POST', 'GET'])
def get_film_region_distribution():
    """
    获取演员出演电影的地区分布
    :return:
    """
    if request.method == 'GET':
        actor_id = request.args.get('actor_id')
        # 根据演员的id去查询演员的电影
        film_info = Films.query.filter_by(actor_id=actor_id).all()
        db.session.close()
        if film_info:
            # 记录电影的地区列表
            film_region_list = []
            for film in film_info:
                if film.film_region == '':
                    film_region_list.append('无')
                else:
                    film_region_info = film.film_region.split(' / ')
                    film_region_list.extend(film_region_info)
            # 元素计数
            film_region_dict = dict(collections.Counter(film_region_list))

            final_dict = {}
            i = 0
            for k,v in film_region_dict.items():
                region_dict = {'region': k, 'count': v}
                final_dict[i] = region_dict
                i += 1
            """
            for example {0: {'region': '中国大陆', 'count': 50}, 1: {'region': '中国香港', 'count': 1}, 2: {'region': '中国台湾', 'count': 1}, 3: {'region': '中国', 'count': 1}, 4: {'region': '无', 'count': 5}}

            """
            print(final_dict)
            return final_dict
        else:
            return '没有查询到电影的地区信息'


@actor_blue.route('/getChangedFilmTypeByTime', methods=['POST', 'GET'])
def get_changed_film_type_by_time():
    """
    按照年份给出演员出演电影的类型
    request.args.get('actor_id')
    :return:
    """
    if request.method == 'GET':
        actor_id = request.args.get('actor_id')
        # 根据演员的id去查询演员的电影年份
        film_list = Films.query.filter_by(actor_id=actor_id).all()
        time_list = []
        for film in film_list:
            time_list.append(film.film_year)
        db.session.close()
        film_type_by_time_dict = {}
        i = 0
        for time in sorted(set(time_list), reverse=True):
            time_dict = get_film_type_distribution(time=time)
            actor_film_type_by_time_dict = {'year': time, 'data': time_dict}
            film_type_by_time_dict[i] = actor_film_type_by_time_dict
            i += 1
        print(film_type_by_time_dict)
        """
        {'2020': {'歌舞': 1}, '2019': {'剧情': 3, '动作': 1}, '2018': {'爱情': 2, '奇幻': 1, '剧情': 1, '音乐': 1, '歌舞': 1}, '2017': {'剧情': 3, '爱情': 1}, '2016': {'喜剧': 2, '奇幻': 2, '武侠': 2, '剧情': 2}, '2015': {'剧情': 3, '惊悚': 1}, '2014': {'剧情': 2, '历史': 1}, '2013': {'剧情': 2}, '2012': {'悬疑': 1, '剧情': 1}, '2011': {'剧情': 1, '爱情': 1}, '2010': {'剧情': 2, '历史': 1, '无': 1}, '2009': {'无': 1, '剧情': 1, '儿童': 1}, '2008': {'喜剧': 1}, '2005': {'喜剧': 2, '家庭': 1, '剧情': 2, '历史': 1, '无': 1}, '2004': {'无': 1}}

        """
        return film_type_by_time_dict
