import pandas as pd


class Recommend:
    def __init__(self, current_ator, like_actors):
        self.current_ator = current_ator
        self.like_actors = like_actors

    def compute_similarity(self):
        return

    def recommend_actor(self):
        return

    def init_data(self):
        return

def init_actor_similarity_dataset():
    """
    性别、年龄段、平均电影评分、平均电影评论、获奖个数、电影部数、职业多样化、出生地、星座、
    平均五星率、平均四星率、平均三星率、平均两星率、平均一星率、是否国际化、电影类型总数、每种类型占比
    :return:
    """
    # # 查询演员的所有信息
    # actors = db.session.query(Actors).all()
    # # 针对每个演员，获取以及计算中间可能需要的数据
    # for actor in actors:
    #     dd
    list_l = [[1, 3, 3, 5, 4], [11, 7, 15, 13, 9], [4, 2, 7, 9, 3], [15, 11, 12, 6, 11]]
    df = pd.DataFrame(list_l, columns=['a', 'b', 'c', 'd', 'e'],)
    print(df)
    df.to_csv('G:/我是测试.csv',index=False)



if __name__ == '__main__':
    print("hahaha")
    init_actor_similarity_dataset()