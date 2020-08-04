import collections
import math
import os
import datetime
import requests
from flask import Blueprint, jsonify
from flask import request
from flask import render_template
from sqlalchemy import func, and_

from .film import get_films_by_actor_id
from .. import db
from ..apriori import Apriori
from ..models import Actors, Awards, Films
import pandas as pd
import numpy as np

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
def get_film_type_distribution(time=0, actor_id=0):
    """
    获取演员出演电影的类型分布
    :return:
    """
    if request.method == 'GET':
        if request.args.get('actor_id'):
            if 'moreButton' not in request.args.get('actor_id'):
                actor_id = request.args.get('actor_id')
            else:
                actor_id = request.args.get('actor_id').replace('moreButton', '')
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
                    film_type_list.extend(film_type_info[0:-1])
            # 元素计数
            film_type_dict = dict(collections.Counter(film_type_list))
            final_dict = {}
            i = 0
            for k, v in film_type_dict.items():
                type_dict = {'type': k, 'count': v}
                final_dict[i] = type_dict
                i += 1
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
        actor_id = request.args.get('actor_id').replace('moreButton', '')
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
        actor_id = request.args.get('actor_id').replace('moreButton', '')
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
        return film_type_by_time_dict


@actor_blue.route('/getAwards', methods=['POST', 'GET'])
def get_awards(id=''):
    if request.method == 'GET':
        actor_id = request.args.get('actor_id').replace('moreButton', '')
    else:
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
        # 演员出演电影类型随时间变化
        film_type = get_changed_film_type_by_time()
        # 演员的电影信息
        films = get_films_by_actor_id()
        colorful = ['bg-primary', 'bg-pink', 'bg-warning', 'bg-info', 'bg-purple', 'bg-success', 'bg-danger']
        return render_template('actorinfo.html', Films=films, FilmType=film_type, Color=colorful, Award=award_info,
                               avatar=avatar, age=age, Chinese_name=Chinese_name,
                               English_name=English_name, Actor=actor_info, frequent_cooperation=frequent_cooperation)


def get_actor_age_group(actor_birthday):
    """
    判断演员的年龄段
    :param actor_birthday: 例如1998-02-05，生日
    :return: 年龄段 20-30组、30-40组、40-50组
    """
    age = get_actor_age_by_birthday(actor_birthday)
    if 0 < age < 30:
        return 'after_90s'
    elif 30 <= age < 40:
        return 'after_80s'
    else:
        return 'after_70s'


def actor_is_multi_career(actor_career):
    """
    判断演员是否拥有多个职业
    :param actor_career: 职业字符串
    :return: 1多职业，0单职业
    """
    if actor_career.find('/') != -1:
        return 1
    else:
        return 0


def get_actor_faction(actor_birthplace):
    '''
    根据演员的出生地判断演员属于北方派系还是南方派系
    :param actor_birthplace: 出生地
    :return: 派系 north  south
    '''
    faction = actor_birthplace.split(',')[1]
    north = '北京市、天津市、内蒙、新疆、河北、甘肃、宁夏、山西、陕西、青海、山东、河南、安徽、辽宁、吉林、黑龙江'
    south = '江苏、浙江、上海、湖北、湖南、四川、重庆市、贵州、云南、广西、江西、福建、广东、海南、西藏、台湾、香港、澳门、三沙'
    if north.find(faction) != -1:
        return 'north'
    elif south.find(faction) != -1:
        return 'south'


def get_actor_horoscope_code(actor_horoscope):
    list_horoscope = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']
    for key, value in enumerate(list_horoscope):
        if value == actor_horoscope:
            return key + 1


def get_actor_is_international(actor_id):
    """
    判断演员是否是国际化类型（出演的电影曾在中国以外地区播放）
    :param actor_id: 演员id
    :return: 1国际化，0非国际化
    """
    films = Films.query.filter(
        and_(actor_id == Films.actor_id, Films.film_region.like('%' + '/' + '%')))
    db.session.close()
    if films:
        for film in films:
            region = film.film_region.split(' / ')
            for item in region:
                if item.find('中国') == -1:
                    return 1
        return 0
    else:
        return 0


def get_actor_film_avg_star(actor_id, star, total):
    films = Films.query.filter_by(actor_id=actor_id)
    db.session.close()
    score = 0
    if star == 5:
        for film in films:
            score += float(film.film_star_ratio_five.replace('%', ''))
    elif star == 4:
        for film in films:
            score += float(film.film_star_ratio_four.replace('%', ''))
    elif star == 3:
        for film in films:
            score += float(film.film_star_ratio_three.replace('%', ''))
    elif star == 2:
        for film in films:
            score += float(film.film_star_ratio_two.replace('%', ''))
    elif star == 1:
        for film in films:
            score += float(film.film_star_ratio_one.replace('%', ''))
    return score / total / 100


def get_actor_film_type_count(actor_id):
    films = Films.query.filter_by(actor_id=actor_id)
    db.session.close()
    list_type = []
    for film in films:
        type = film.film_type
        if type == '':
            list_type.append('no')
        else:
            new_type = type.split(' ')[0:-1]
            list_type = sorted(list(set(list_type).union(set(new_type))))
    return len(list_type)


def get_actor_film_type_proportion(actor_id, actor_film_sum):
    """
    获得演员的电影类型占比表
    :param actor_id: 演员id
    :param actor_film_sum: 该演员的电影总数
    :return: 类型分布表
    """
    type_dict = {'剧情': 0, '爱情': 0, '动作': 0, '科幻': 0, '冒险': 0, '悬疑': 0, '喜剧': 0, '惊悚': 0, '传记': 0,
                 '动画': 0, '家庭': 0, '奇幻': 0, '武侠': 0, '灾难': 0, '歌舞': 0, '历史': 0, '音乐': 0, '短片': 0,
                 '儿童': 0, '戏曲': 0, '犯罪': 0, '战争': 0, '西部': 0, '运动': 0, '真人秀': 0, '纪录片': 0, '脱口秀': 0,
                 '古装': 0, '恐怖': 0, '情色': 0, '同性': 0, '无': 0
                 }
    final_dict = get_film_type_distribution(actor_id=actor_id)
    for key, value in final_dict.items():
        type_dict[value['type']] = value['count'] / actor_film_sum
    print(len(type_dict))
    print(type_dict)
    return list(type_dict.values())


film_type_c2e_dict = {'剧情': 'type_feature', '爱情': 'type_romance', '动作': 'type_action', '科幻': 'type_science', '冒险': 'type_adventure', '悬疑': 'type_suspense', '喜剧': 'type_comedy', '惊悚': 'type_thriller', '传记': 'type_biography',
                      '动画': 'type_cartoon', '家庭': 'type_family', '奇幻': 'type_fantasy', '武侠': 'type_sowordsmen', '灾难': 'type_disaster', '歌舞': 'type_dance', '历史': 'type_history', '音乐': 'type_music', '短片': 'type_short',
                      '儿童': 'type_children', '戏曲': 'type_opera', '犯罪': 'type_crime', '战争': 'type_war', '西部': 'type_western', '运动': 'type_sport', '真人秀': 'type_reality', '纪录片': 'type_documentary', '脱口秀': 'type_talkshow',
                      '古装': 'type_costume', '恐怖': 'type_horror', '情色': 'type_blue', '同性': 'type_samesex', '无':'type_no'
                      }

@actor_blue.route('/get', methods=['POST', 'GET'])
def init_actor_similarity_dataset():
    """
    性别、年龄段、平均电影评分、平均电影评论、获奖个数、电影部数、职业多样化、出生地、星座、
    平均五星率、平均四星率、平均三星率、平均两星率、平均一星率、是否国际化、电影类型总数、每种类型占比
    :return:
    """
    # 查询演员的所有信息
    actors = db.session.query(Actors).all()
    # 存放该演员的所有特征信息
    list_actor_feature = []
    # 特征名
    feature_name = ['actor_id', 'actor_gender', 'actor_age_group', 'actor_avg_films_score', 'actor_avg_comments_sum',
                    'actor_award_sum', 'actor_film_sum', 'actor_multi_career', 'actor_birthplace_faction', 'actor_horoscope_code',
                    'actor_film_avg_five_star', 'actor_film_avg_four_star', 'actor_film_avg_three_star', 'actor_film_avg_two_star', 'actor_film_avg_one_star',
                    'actor_international', 'actor_film_type_sum',
                    'type_feature', 'type_romance', 'type_action', 'type_science', 'type_adventure', 'type_suspense', 'type_comedy', 'type_thriller', 'type_biography',
                    'type_cartoon', 'type_family', 'type_fantasy', 'type_sowordsmen', 'type_disaster', 'type_dance', 'type_history', 'type_music', 'type_short',
                    'type_children', 'type_opera', 'type_crime', 'type_war', 'type_western', 'type_sport', 'type_reality', 'type_documentary', 'type_talkshow',
                    'type_costume', 'type_horror', 'type_blue', 'type_samesex', 'type_no']
    # 针对每个演员，获取以及计算中间可能需要的数据
    for actor in actors:
        # 存放该演员的所有特征信息
        actor_feature = []
        actor_feature.append(actor.actor_id)
        # 演员性别
        actor_gender = actor.actor_gender
        actor_feature.append(actor_gender)
        # 演员年龄段
        actor_age_group = get_actor_age_group(actor.actor_birthday)
        actor_feature.append(actor_age_group)
        # 演员平均电影评分
        actor_avg_films_score = actor.actor_avg_films_score
        actor_feature.append(actor_avg_films_score)
        # 演员平均电影评论
        actor_avg_comments_sum = actor.actor_avg_comments_sum
        actor_feature.append(actor_avg_comments_sum)
        # 演员获奖个数
        actor_award_sum = db.session.query(func.count(Awards.id)).filter(Awards.actor_id == actor.actor_id).scalar()
        actor_feature.append(actor_award_sum)
        # 演员电影部数
        actor_film_sum = db.session.query(func.count(Films.id)).filter(Films.actor_id == actor.actor_id).scalar()
        actor_feature.append(actor_film_sum)
        # 演员职业是否多样化
        actor_multi_career = actor_is_multi_career(actor.actor_career)
        actor_feature.append(actor_multi_career)
        # 演员出生地，南、北方
        actor_birthplace_faction = get_actor_faction(actor.actor_birthplace)
        actor_feature.append(actor_birthplace_faction)
        # 演员星座
        actor_horoscope_code = get_actor_horoscope_code(actor.actor_horoscope)
        actor_feature.append(actor_horoscope_code)
        # 电影平均五星率
        actor_film_avg_five_star = get_actor_film_avg_star(actor.actor_id, 5, actor_film_sum)
        actor_feature.append(actor_film_avg_five_star)
        # 电影平均四星率
        actor_film_avg_four_star = get_actor_film_avg_star(actor.actor_id, 4, actor_film_sum)
        actor_feature.append(actor_film_avg_four_star)
        # 电影平均三星率
        actor_film_avg_three_star = get_actor_film_avg_star(actor.actor_id, 3, actor_film_sum)
        actor_feature.append(actor_film_avg_three_star)
        # 电影平均两星率、平均一星率、是否国际化、电影类型总数、每种类型占比
        actor_film_avg_two_star = get_actor_film_avg_star(actor.actor_id, 2, actor_film_sum)
        actor_feature.append(actor_film_avg_two_star)
        # 电影平均一星率
        actor_film_avg_one_star = get_actor_film_avg_star(actor.actor_id, 1, actor_film_sum)
        actor_feature.append(actor_film_avg_one_star)
        # 是否国际化
        actor_international = get_actor_is_international(actor.actor_id)
        actor_feature.append(actor_international)
        # 电影类型总数
        actor_film_type_sum = get_actor_film_type_count(actor.actor_id)
        actor_feature.append(actor_film_type_sum)
        # 每种类型占比
        actor_film_type_proportion = get_actor_film_type_proportion(actor.actor_id, actor_film_sum)
        actor_feature.extend(actor_film_type_proportion)

        list_actor_feature.append(actor_feature)
    df = pd.DataFrame(list_actor_feature, columns=feature_name)
    df.to_csv('/static/data/actor_similarity_data.csv', index=False)
