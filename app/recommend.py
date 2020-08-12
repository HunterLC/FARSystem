import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer, MinMaxScaler
from scipy.linalg import norm


class Recommend:
    def __init__(self, data_path, current_ator, like_actors):
        # 当前演员id
        self.current_ator = int(current_ator)
        # 当前用户喜欢的演员id列表
        self.like_actors = like_actors
        # 演员特征数据地址
        self.data_path = data_path
        # id索引df
        self.df_id = None

    def run(self):
        df = self.init_data()
        df = self.preprocess(df)
        result1, result2 = self.compute_similarity(df)
        print(result1)
        print(result2)
        result1 = np.array(result1)
        result2 = np.array(result2)
        np.sort(result1)
        np.sort(result2)
        print(np.argsort(-result1))  # 逆序输出索引，从大到小,余弦相似度越大越相似
        print(np.argsort(result2))  # 正序输出索引，从小到大，欧式距离越小越相似
        return result1, result2

    def compute_similarity(self, df):
        result1 = []
        result2 = []
        # 根据当前用户的id获得其在列表中的索引
        index = self.df_id[self.df_id.values == self.current_ator].index[0]
        current = df.loc[index].values
        for index, row in df.iterrows():
            # 余弦相似度
            row = row.values
            score = np.dot(current, row) / (norm(current) * norm(row))
            # 欧式距离
            distance = np.sqrt(np.sum(np.square(current - row)))
            result1.append(score)
            result2.append(distance)
        return result1, result2

    def recommend_actor(self):
        return

    def preprocess(self, df):
        # 特征预处理
        # step1：将object编码
        obj_attrs = []
        feature_attr = df.columns.tolist()
        feature_attr.remove('actor_id')
        for attr in feature_attr:
            # 添加离散数据列
            if df.dtypes[attr] == np.dtype(object):
                obj_attrs.append(attr)
        if len(obj_attrs) > 0:
            # 转为哑变量
            df = pd.get_dummies(df, columns=obj_attrs)
        # step2: 去除id行，并针对部分行进行0-1规范化
        self.df_id = df['actor_id']
        df.drop(['actor_id'], axis=1, inplace=True)
        # 行归一化
        # df = Normalizer().fit_transform(df)

        # 全局0-1区间变换
        # new = MinMaxScaler().fit_transform(df.values)
        # df_new = pd.DataFrame(new)  # 将array转化为dataframe
        # df_new.columns = df.columns  # 命名标题行

        # 部分数据0-1规范化 actor_avg_films_score, actor_avg_comments_sum, actor_award_sum, actor_film_sum, actor_film_type_sum
        df['actor_avg_films_score'] = df['actor_avg_films_score'].apply(
            lambda x: (x - df['actor_avg_films_score'].min())/(
                        df['actor_avg_films_score'].max() - df['actor_avg_films_score'].min()))
        df['actor_avg_comments_sum'] = df['actor_avg_comments_sum'].apply(
            lambda x: (x - df['actor_avg_comments_sum'].min()) / (
                        df['actor_avg_comments_sum'].max() - df['actor_avg_comments_sum'].min()))
        df['actor_award_sum'] = df['actor_award_sum'].apply(
            lambda x: (x - df['actor_award_sum'].min()) / (
                        df['actor_award_sum'].max() - df['actor_award_sum'].min()))
        df['actor_film_sum'] = df['actor_film_sum'].apply(
            lambda x: (x - df['actor_film_sum'].min()) / (
                        df['actor_film_sum'].max() - df['actor_film_sum'].min()))
        df['actor_film_type_sum'] = df['actor_film_type_sum'].apply(
            lambda x: (x - df['actor_film_type_sum'].min()) / (
                        df['actor_film_type_sum'].max() - df['actor_film_type_sum'].min()))

        return df

    def init_data(self):
        """
        读取演员数据
        :return:
        """
        df = pd.read_csv(self.data_path)
        return df


if __name__ == '__main__':
    result1, result2 = Recommend('../static/data/actor_similarity_data.csv', 1314124, 6).run()



