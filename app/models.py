import random

from . import db


class Actors(db.Model):
    """
    演员表
    """
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_id = db.Column(db.Integer)
    actor_c_name = db.Column(db.String(64))
    actor_img = db.Column(db.String(255))
    actor_gender = db.Column(db.String(10))
    actor_horoscope = db.Column(db.String(64))
    actor_birthday = db.Column(db.String(64))
    actor_birthplace = db.Column(db.String(64))
    actor_career = db.Column(db.String(64))
    actor_avg_films_score = db.Column(db.Float)
    actor_avg_comments_sum = db.Column(db.Integer)

    def to_json(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'actor_c_name': self.actor_c_name,
            'actor_img': self.actor_img,
            'actor_gender': self.actor_gender,
            'actor_horoscope': self.actor_horoscope,
            'actor_birthday': self.actor_birthday,
            'actor_birthplace': self.actor_birthplace,
            'actor_career': self.actor_career,
            'actor_avg_films_score': self.actor_avg_films_score,
            'actor_avg_comments_sum': self.actor_avg_comments_sum
        }

    def set_avg_score_and_comments(self, actor_avg_films_score, actor_avg_comments_sum):
        self.actor_avg_films_score = actor_avg_films_score
        self.actor_avg_comments_sum = actor_avg_comments_sum


class Awards(db.Model):
    """
    演员获奖表
    """
    __tablename__ = 'awards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_id = db.Column(db.Integer)
    award_year = db.Column(db.String(10))
    award_ceremony = db.Column(db.String(64))
    award_name = db.Column(db.String(64))
    award_film = db.Column(db.String(64))

    def to_json(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'award_year': self.award_year,
            'award_ceremony': self.award_ceremony,
            'award_name': self.award_name,
            'award_film': self.award_film
        }


class Films(db.Model):
    """
    电影表
    """
    __tablename__ = 'films'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    actor_id = db.Column(db.Integer)
    film_id = db.Column(db.Integer)
    film_name = db.Column(db.String(64))
    film_year = db.Column(db.String(10))
    film_img = db.Column(db.String(255))
    film_director = db.Column(db.String(255))
    film_protagonist = db.Column(db.String(500))
    film_type = db.Column(db.String(64))
    film_region = db.Column(db.String(64))
    film_score = db.Column(db.Float)
    film_comments_sum = db.Column(db.Integer)
    film_star_ratio_five = db.Column(db.String(10))
    film_star_ratio_four = db.Column(db.String(10))
    film_star_ratio_three = db.Column(db.String(10))
    film_star_ratio_two = db.Column(db.String(10))
    film_star_ratio_one = db.Column(db.String(10))

    def to_json(self):
        return {
            'id': self.id,
            'actor_id': self.actor_id,
            'film_id': self.film_id,
            'film_name': self.film_name,
            'film_year': self.film_year,
            'film_img': self.film_img,
            'film_director': self.film_director,
            'film_protagonist': self.film_protagonist,
            'film_type': self.film_type,
            'film_region': self.film_region,
            'film_score': self.film_score,
            'film_comments_sum': self.film_comments_sum,
            'film_star_ratio_five': self.film_star_ratio_five,
            'film_star_ratio_four': self.film_star_ratio_four,
            'film_star_ratio_three': self.film_star_ratio_three,
            'film_star_ratio_two': self.film_star_ratio_two,
            'film_star_ratio_one': self.film_star_ratio_one
        }


class Users(db.Model):
    """
    用户表
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(255))
    user_email = db.Column(db.String(64))
    user_gender = db.Column(db.String(10))
    user_password = db.Column(db.String(64))
    user_image = db.Column(db.String(255))
    user_desc = db.Column(db.String(255))

    def __init__(self, user_name, user_email, user_password):
        self.user_id = random.randint(100000, 999999)
        self.user_name = user_name
        self.user_email = user_email
        self.user_gender = 'unknow'
        self.user_password = user_password
        self.user_image = r'\static\dist\img\user4-128x128.jpg'
        self.user_desc = 'FAR'

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'user_gender': self.user_gender,
            'user_password': self.user_password,
            'user_image': self.user_image,
            'user_desc': self.user_desc
        }


class Likes(db.Model):
    """
    用户喜爱演员表
    """
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    actor_id = db.Column(db.Integer)

    def __init__(self, user_id, actor_id):
        self.user_id = user_id
        self.actor_id = actor_id

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'actor_id': self.actor_id
        }
