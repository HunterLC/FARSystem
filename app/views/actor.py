import collections
import math
import os
import datetime
import requests
from flask import Blueprint
from flask import request
from flask import render_template
from .. import db
from ..apriori import Apriori
from ..models import Actors, Awards, Films

actor_blue = Blueprint('actor', __name__)


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
            for k, v in film_region_dict.items():
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
        return film_type_by_time_dict


@actor_blue.route('/getAwards', methods=['POST', 'GET'])
def get_awards(id=''):
    if request.method == 'GET':
        print('hhh11')
        actor_id = request.args.get('actor_id').replace('moreButton', '')
    else:
        print('hhh')
        actor_id = id
    # 根据演员的id去查询演员的获奖信息
    award_info = Awards.query.filter_by(actor_id=actor_id).all()
    if award_info is None:
        return {
            'count': 0,
            'data': '无获奖信息'
        }
    else:
        count = len(award_info)
        time_list = []
        for award in award_info:
            time_list.append(award.award_year)
        j = 0
        final_dict = {}
        for time in sorted(set(time_list), reverse=True):
            i = 0
            award_by_time_dict = {}
            for award in award_info:
                if time == award.award_year:
                    award_by_time_dict[i] = award.to_json()
                    i += 1
            final_dict[j] = {'year': time, 'data': award_by_time_dict}
            j += 1
        return {
            'count': count,
            'data': final_dict
        }


@actor_blue.route('/downloadActorImg', methods=['POST', 'GET'])
def download_actor_img():
    actors = db.session.query(Actors).all()
    db.session.close()
    for actor in actors:
        img_name = actor.actor_img.split('/')[-1]
        img_path = r'E:\PythonCode\FARSystem\static\image\actor\{}'.format(img_name)
        print(img_path)
        try:
            if not os.path.exists(img_path):
                r = requests.get(actor.actor_img)
                with open(img_path, 'wb') as f:
                    f.write(r.content)
                    f.close()
                    print("文件保存成功")
            else:
                print("文件已存在")
        except Exception as err:
            print(err)
    return 'success'


def get_frequent_cooperation_by_id(name, id, min_support=5):
    """
    根据演员的姓名和演员id，利用Apriori算法获得合作最多的一名演员姓名
    :param name: 演员的姓名，含有英文，例如【杨紫 Andy Yang】
    :param id: 演员的唯一标识
    :return: 合作最多的一名演员姓名
    """
    # 演员合作数据列表
    dataset_cooperation = []
    # 中文名
    chinese_name = name.split(' ')[0]
    films = Films.query.filter_by(actor_id=id).all()
    db.session.close()
    for film in films:
        item = film.film_protagonist.split(' ')[:-1]
        dataset_cooperation.append(item)
    # 频繁项集，支持度，关联规则
    L, support_data, rule_list = Apriori(dataset=dataset_cooperation, min_support=min_support, min_conf=0.01).apriori()
    for rule in rule_list:
        # 寻找由该演员推导的置信度最高的那位演员姓名
        if chinese_name == list(rule[0])[0]:
            return list(rule[1])[0]


def get_actor_age_by_birthday(actor_birthday):
    """
    根据字符时间计算年龄
    :param actor_birthday: 演员出生日期 YYYY-mm-dd
    :return: 年龄
    """
    birthday = datetime.datetime.strptime(actor_birthday, '%Y-%m-%d')
    today = datetime.datetime.today()
    try:
        temp = birthday.replace(year=today.year)
    # 异常出现在2月29日，且当年并非闰年
    except ValueError:
        temp = birthday.replace(year=today.year, day=birthday.day - 1)
    if temp > today:
        return today.year - birthday.year - 1
    else:
        return today.year - birthday.year


@actor_blue.route('/getActorInfo', methods=['POST', 'GET'])
def get_actor_info():
    if request.method == 'GET':
        # 前端传过来的id格式中含有前缀moreButton
        actor_id = request.args.get('actor_id').replace('moreButton', '')
        # 根据演员的id去查询演员的基本信息
        actor_info = Actors.query.filter_by(actor_id=actor_id).all()[0]
        db.session.close()
        # 演员中文名
        Chinese_name = actor_info.actor_c_name.split(' ')[0]
        # 演员英文名
        English_name = actor_info.actor_c_name.replace(Chinese_name, '').lstrip()
        # 合作最多演员名字
        min_cooperation_times = 5
        # 年龄
        age = get_actor_age_by_birthday(actor_info.actor_birthday)
        # 头像编号
        avatar = actor_info.actor_img.split('/')[-1]
        while (True):
            frequent_cooperation = get_frequent_cooperation_by_id(actor_info.actor_c_name, actor_id,
                                                                  min_support=min_cooperation_times)
            if frequent_cooperation is not None:
                break
            min_cooperation_times -= 1
        # 演员获奖信息
        award_info = get_awards(actor_id)
        print(award_info)
        colorful = ['bg-primary', 'bg-pink', 'bg-warning', 'bg-info', 'bg-purple', 'bg-success', 'bg-danger']
        return render_template('actorinfo.html', Color=colorful, Award=award_info, avatar=avatar, age=age, Chinese_name=Chinese_name,
                               English_name=English_name, Actor=actor_info, frequent_cooperation=frequent_cooperation)
