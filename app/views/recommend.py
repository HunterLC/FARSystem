from flask import Blueprint, redirect, url_for
from flask import request
from flask import render_template
from flask import session
from sqlalchemy import and_

from .. import db
from app.models import Actors, Users, Likes
from ..recommend import Recommend

recommend_blue = Blueprint('recommend', __name__)


@recommend_blue.route('/', methods=['GET', 'POST'])
def start():
    if request.method == "GET":
        likes = db.session.query(Likes).all()
        user_item = Recommend(sim_algorithm=0, top_k_user=3, top_k_actor=3, user_id=session['userid'],
                              users_like=likes).run_collaborative_filtering()
        # 猜你喜欢
        guess_actor = []
        for key, value in user_item.items():
            actor = db.session.query(Actors).filter(Actors.actor_id == int(key)).all()[0]
            guess_actor.append(actor)
        db.session.close()
        for guess in guess_actor:
            guess.actor_c_name = guess.actor_c_name.split(' ')[0]
            guess.actor_img = guess.actor_img.split('/')[-1]
        return render_template("recommend.html", Guess=guess_actor)


@recommend_blue.route('/recommendActor', methods=['GET', 'POST'])
def recommend_actor():
    if request.method == "GET":
        # 存储用户输入的数据
        feature_dict = {}
        # 电影类型
        film_type_select = request.args.get('filmTypeSelect')
        feature_dict[film_type_select] = 1
        # 演员性别
        actor_gender = request.args.get('genderSelect')
        if actor_gender != "":
            feature_dict['actor_gender'] = actor_gender
        # 演员年龄段
        actor_age_group = request.args.get('ageSelect')
        feature_dict['actor_age_group'] = actor_age_group
        # 演员所属地域
        actor_birthplace_faction = request.args.get('areaSelect')
        if actor_birthplace_faction != "":
            feature_dict['actor_birthplace_faction'] = actor_birthplace_faction
        # 是否国际化
        actor_international = request.args.get('internationalSelect')
        if actor_international != "":
            feature_dict['actor_international'] = actor_international
        # 是否多职业
        actor_multi_career = request.args.get('multiCareerSelect')
        if actor_multi_career != "":
            feature_dict['actor_multi_career'] = actor_multi_career
        # 演员星座
        actor_horoscope_code = request.args.get('horoscopeSelect')
        if actor_horoscope_code != "":
            feature_dict['actor_horoscope_code'] = actor_horoscope_code
        # 关心星率
        star_rate_select = request.args.get('starRateSelect')
        if star_rate_select != "":
            feature_dict[star_rate_select] = 1
        # 平均评分
        actor_avg_films_score = request.args.get('range_avg_score')
        feature_dict['actor_avg_films_score'] = actor_avg_films_score
        # 电影总数
        actor_film_sum = request.args.get('range_total_films')
        feature_dict['actor_film_sum'] = actor_film_sum
        # 获奖总数
        actor_award_sum = request.args.get('range_total_awards')
        feature_dict['actor_award_sum'] = actor_award_sum
        # 平均评论数
        actor_avg_comments_sum = request.args.get('range_avg_comments')
        feature_dict['actor_avg_comments_sum'] = actor_avg_comments_sum
        result = Recommend(r'E:\PythonCode\FARSystem\static\data\actor_similarity_data.csv', current_actor=1314124,
                  like_actors=[1314124], input_dict=feature_dict).run()
        # 猜你喜欢
        guess_actor = []
        for key, value in result.items():
            actor = db.session.query(Actors).filter(Actors.actor_id == int(key)).all()[0]
            guess_actor.append(actor)
        db.session.close()
        result_list = {}
        i = 1
        for guess in guess_actor:
            result_dict = {}
            result_dict[str(guess.actor_id)] = {}
            result_dict[str(guess.actor_id)]['img'] = guess.actor_img.split('/')[-1]
            result_dict[str(guess.actor_id)]['name'] = guess.actor_c_name.split(' ')[0]
            result_list[str(i)] = result_dict
            print(result_dict)
            i += 1
        print(result_list)
        return result_list


@recommend_blue.route('/a', methods=['GET', 'POST'])
def a():
    likes = db.session.query(Likes).all()
    db.session.close()
    user_item = Recommend(sim_algorithm=0, top_k_user=3, top_k_actor=3, user_id=session['userid'],
                          users_like=likes).run()
    return user_item
