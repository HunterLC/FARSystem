from math import sqrt

import pandas as pd
import numpy as np
from sklearn.preprocessing import Normalizer, MinMaxScaler
from scipy.linalg import norm


class Recommend:
    def __init__(self, data_path=r'E:\PythonCode\FARSystem\static\data\actor_similarity_data.csv', current_actor=0, like_actors=None,
                 input_dict=None, sim_algorithm=0, top_k_user=3, top_k_actor=3, user_id=None, users_like=None):
        # 当前演员id
        self.current_actor = int(current_actor)
        # 当前用户喜欢的演员id列表
        self.like_actors = like_actors
        # 演员特征数据地址
        self.data_path = data_path
        # id索引df
        self.df_id = None
        # 用户输入的特征字典
        self.feature_dict = input_dict
        # 相似度算法，默认为余弦相似度
        self.algorithm = sim_algorithm
        self.top_k_user = top_k_user
        self.top_k_actor = top_k_actor
        self.user = user_id
        self.users_like = users_like

    def run(self):
        df = self.init_data()
        df = self.preprocess(df)
        result_dict = self.recommend_actor(df)
        return result_dict

    def run_collaborative_filtering(self):
        df = self.init_data()
        df = self.preprocess(df)
        result_dict = self.collaborative_filtering_recommend(df)
        return result_dict

    def compute_2_actors(self, df, actor_1, actor_2):
        # 根据当前用户的id获得其在列表中的索引
        index_1 = self.df_id[self.df_id.values == int(actor_1)].index[0]
        current_1 = df.loc[index_1].values
        index_2 = self.df_id[self.df_id.values == int(actor_2)].index[0]
        current_2 = df.loc[index_2].values
        sim_score = 0
        # 余弦相似度
        if self.algorithm == 0:
            sim_score = np.dot(current_1, current_2) / (norm(current_1) * norm(current_2))
        # 欧式距离
        elif self.algorithm == 1:
            sim_score = np.sqrt(np.sum(np.square(current_1 - current_2)))
        return sim_score


    def cal_actor_similarity(self, df):
        # 相似度分数
        result_score = []
        # 相似度索引，越靠前则代表越相似
        result_index = []

        # 根据当前演员的id获得其在列表中的索引
        index = self.df_id[self.df_id.values == self.current_actor].index[0]
        current = df.loc[index].values
        if self.feature_dict is not None:
            df.drop(index=index, inplace=True)
        for index, row in df.iterrows():
            row = row.values
            score = 0
            # 余弦相似度
            if self.algorithm == 0:
                score = np.dot(current, row) / (norm(current) * norm(row))
            # 欧式距离
            elif self.algorithm == 1:
                score = np.sqrt(np.sum(np.square(current - row)))
            result_score.append(score)

        # 计算相似度索引，越靠前则代表越相似
        result1 = np.array(result_score)
        np.sort(result1)
        # 余弦相似度
        if self.algorithm == 0:
            result_index = np.argsort(-result1)  # 逆序输出索引，从大到小,余弦相似度越大越相似
        # 欧式距离
        elif self.algorithm == 1:
            result_index = np.argsort(result1)  # 正序输出索引，从小到大，欧式距离越小越相似
        return result_score, result_index

    def recommend_actor(self, df):
        # 计算相似度分数
        score, index = self.cal_actor_similarity(df)
        print(score)
        print(index)
        result_dict = {}
        # 进行演员推荐系统，就算是用户喜欢过的演员依旧会推荐
        # list_id = []
        # for item in index:
        #     actor_id = str(self.df_id.loc[item])
        #     list_id.append(actor_id)
        list_id = self.df_id.tolist()
        result_dict = dict(zip(list_id, score))
        print(result_dict)
        if self.feature_dict is not None:
            result_dict = dict(sorted(result_dict.items(), key=lambda item: item[1], reverse=True)[:self.top_k_actor])
        else:
            result_dict = dict(sorted(result_dict.items(), key=lambda item: item[1], reverse=True)[1:self.top_k_actor+1])
        print(result_dict)
        return result_dict

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

        standard_list = ['actor_avg_films_score', 'actor_avg_comments_sum', 'actor_award_sum', 'actor_film_sum',
                         'actor_film_type_sum']
        for feature in standard_list:
            if feature in df.columns.values.tolist():
                # 算法目的是寻找与用户输入最为接近的数据，数值越接近则权值最大，例如[0,20,50,100]，当用户输入40时，则50的权重最大
                if self.feature_dict is not None:
                    df[feature] = df[feature].apply(
                        lambda x: df[feature].max() - abs(x - self.feature_dict[feature]))
                # 数据0-1规范化
                df[feature] = df[feature].apply(
                    lambda x: (x - df[feature].min()) / (
                            df[feature].max() - df[feature].min()))

        # df['actor_avg_films_score'] = df['actor_avg_films_score'].apply(
        #     lambda x: (x - df['actor_avg_films_score'].min()) / (
        #             df['actor_avg_films_score'].max() - df['actor_avg_films_score'].min()))
        # df['actor_avg_comments_sum'] = df['actor_avg_comments_sum'].apply(
        #     lambda x: (x - df['actor_avg_comments_sum'].min()) / (
        #             df['actor_avg_comments_sum'].max() - df['actor_avg_comments_sum'].min()))
        # df['actor_award_sum'] = df['actor_award_sum'].apply(
        #     lambda x: (x - df['actor_award_sum'].min()) / (
        #             df['actor_award_sum'].max() - df['actor_award_sum'].min()))
        # df['actor_film_sum'] = df['actor_film_sum'].apply(
        #     lambda x: (x - df['actor_film_sum'].min()) / (
        #             df['actor_film_sum'].max() - df['actor_film_sum'].min()))
        # df['actor_film_type_sum'] = df['actor_film_type_sum'].apply(
        #     lambda x: (x - df['actor_film_type_sum'].min()) / (
        #             df['actor_film_type_sum'].max() - df['actor_film_type_sum'].min()))

        return df

    def get_feature_names(self):
        """
        获取需要使用的特征
        :return:
        """
        use_cols = ['actor_id']
        keys_feature = list(self.feature_dict.keys())
        use_cols.extend(keys_feature)
        return use_cols

    def insert_input_data(self, df):
        """
        将用户输入插入到最后一行
        :param df:
        :return:
        """
        feature_data = []
        for feature in df.columns.values.tolist():
            if feature == 'actor_id':
                feature_data.append(19980205)
                self.current_actor = 19980205
            else:
                feature_data.append(self.feature_dict[feature])
        df_new = pd.DataFrame([feature_data])
        df_new.columns = df.columns
        df = pd.concat([df, df_new], axis=0, ignore_index=True)
        return df

    def filter_condition(self, df):
        # 性别为强制匹配项，过滤性别不匹配的用户
        if 'actor_gender' in self.feature_dict.keys():
            gender = self.feature_dict['actor_gender']
            df_new = df[df['actor_gender'] == gender]
            return df_new
        else:
            return df


    def init_data(self):
        """
        读取演员数据
        :return:
        """
        if self.feature_dict is not None:
            # 获取需要使用的特征
            use_cols = self.get_feature_names()
            df = pd.read_csv(self.data_path, usecols=use_cols)
            # 性别为强制匹配项，过滤性别不匹配的用户
            df = self.filter_condition(df)
            # 补充最后一行为新输入的数据
            df = self.insert_input_data(df)
        else:
            df = pd.read_csv(self.data_path)
        return df

    def get_ordered(self):
        """
        建立用户-物品正排表
        :return:
        """
        # 保存用户的id
        user_list = []
        # 用户-物品 正排表
        user_item = {}
        for like in self.users_like:
            user_id = str(like.user_id)
            actor_id = str(like.actor_id)
            if user_id not in user_list:
                # 用户记录去重
                user_list.append(user_id)
                # 初始化物品表
                user_item[user_id] = []
            user_item[user_id].append(actor_id)
        # print('正排表')
        # print(user_item)
        return user_list, user_item

    def remove_duplicates(self, user_item):
        """
        物品去重
        :param user_item:
        :return:
        """
        # 物品去重表
        item_list = []
        for key, value in user_item.items():
            item_list.extend(value)
        item_list = set(item_list)
        # print('去重物品表')
        # print(item_list)
        return item_list

    def get_inverted(self, user_item, item_list):
        """
        建立物品-用户倒排表
        :return:
        """
        # 根据去重物品表建立 物品-用户 倒排表
        item_user = {}
        for item in item_list:
            if item not in item_user.keys():
                # 初始化用户表
                item_user[item] = []
            for key_item, value_item in user_item.items():
                # 如果该物品是用户喜欢的，则在对应物品后面添加该用户id
                if item in value_item:
                    item_user[item].append(key_item)
        # print('物品-用户 表')
        # print(item_user)
        return item_user

    def collaborative_filtering_recommend(self, df):
        """
        协同过滤推荐
        :return:
        """
        # 用户相似度分数
        user_item, sim_user = self.cal_user_similarity()
        if str(self.user) in user_item.keys():
            self.like_actors = user_item[str(self.user)]
            # print('当前用户{}'.format(str(self.user)))
            # print(self.like_actors)
            # 当前用户的id
            if str(self.user) not in sim_user.keys():
                # 当前用户没有与之相似的用户，该用户喜欢了演员,剩下的演员分别与其喜欢的演员计算平均相似度，返回top_k_user
                # 演员id
                id = self.df_id.values.tolist()
                df_origin = df
                # 删除数据框中已经喜欢的演员信息
                for actor_id in self.like_actors:
                    # index = self.df_id[self.df_id.values == int(actor_id)].index[0]
                    # df.drop(index=(index), inplace=True)
                    id.remove(int(actor_id))
                # df = df.reset_index(drop=True)
                new_df_id = pd.Series(id)
                actor_score = []
                for actor_id in self.like_actors:
                    list_score = []
                    for key, value in new_df_id.items():
                        list_score.append(self.compute_2_actors(df_origin, actor_id, value))
                    actor_score.append(np.array(list_score,dtype=np.float64))
                x = actor_score[0]
                print(x)
                for item in actor_score[1:]:
                    x += item
                x = x / len(actor_score)
                score = x
                print(x)
                np.sort(x)
                # 相似度排行索引，越大的越靠前
                result_index = np.argsort(-x)[:self.top_k_actor]
                print(result_index)
                item_score = {}
                for item in result_index:
                    item_score[str(new_df_id[item])] = score[item]
                print(item_score)
                return item_score
            else:
                # 当前用户存在与之相似的用户
                similarity_value = sim_user[str(self.user)]

                if len(similarity_value) >= self.top_k_user:
                    # 相似的用户数量足够时，返回top_k个相似user
                    # print('相似的用户数量足够，返回{}个相似user'.format(str(self.top_k_user)))
                    similarity_value = dict(sorted(similarity_value.items(), key=lambda item: item[1], reverse=True)[
                                            :self.top_k_user])

                # print(similarity_value)
                # 寻找相似用户中，当前用户没有喜欢的物品
                all_like_item = []
                for key, value in similarity_value.items():
                    # 对于每一个相似的用户,获取其喜欢的物品
                    all_like_item.extend(user_item[key])
                # 当前用户喜欢的物品
                curr_like_item = user_item[str(self.user)]
                # 当前用户可能感兴趣的物品
                unlike_item = list(set(all_like_item) - set(curr_like_item))
                # print(unlike_item)
                # 对每一个可能感兴趣的物品，计算推荐分数
                item_score = {}
                for item in unlike_item:
                    # 计算平均用户相似度分数
                    user_score = 0
                    user_count = 0
                    for key_1 in similarity_value.keys():
                        if item in user_item[key_1]:
                            user_score += similarity_value[key_1]
                            user_count += 1
                    user_score = user_score / user_count
                    # print(str(user_score))
                    # 计算平均演员相似度分数
                    actor_score = 0
                    for key_2 in self.like_actors:
                        actor_score += self.compute_2_actors(df, key_2, item)
                    actor_score = actor_score / len(self.like_actors)
                    # print(str(actor_score))

                    # 推荐分数计算
                    recommend_score = user_score * actor_score
                    item_score[item] = recommend_score

                if len(item_score.keys()) >= self.top_k_actor:
                    # 可能感兴趣的数量足够时，返回top_k个actor
                    item_score = dict(sorted(item_score.items(), key=lambda item: item[1], reverse=True)[
                                      :self.top_k_actor])
                else:
                    item_score = dict(sorted(item_score.items(), key=lambda item: item[1], reverse=True))
                print(item_score)
                return item_score
        else:
            # 当前用户没有喜欢任何演员
            print('当前用户没有喜欢任何演员')





    def cal_user_similarity(self):
        """
        计算用户相似度
        :return:
        """
        # 建立用户-物品正排表
        user_list, user_item = self.get_ordered()
        # 物品去重
        item_list = self.remove_duplicates(user_item)
        # 根据去重物品表建立 物品-用户 倒排表
        item_user = self.get_inverted(user_item, item_list)
        # 用户相似度字典
        sim_user = {}
        # 用户个数
        user_sum = len(user_list)
        # print('用户表')
        # print(user_list)

        # 用户间相同喜欢计数
        for index_f in range(0, user_sum - 1):
            for index_s in range(index_f + 1, user_sum):
                if user_list[index_f] not in sim_user.keys():
                    sim_user[user_list[index_f]] = {}
                for key, value in item_user.items():
                    if user_list[index_f] in value and user_list[index_s] in value:
                        print()
                        if user_list[index_s] not in sim_user[user_list[index_f]].keys():
                            sim_user[user_list[index_f]][user_list[index_s]] = 0
                        sim_user[user_list[index_f]][user_list[index_s]] += 1
                        # M[x][y] 值和 M[y][x] 一样
                        if user_list[index_s] not in sim_user.keys():
                            sim_user[user_list[index_s]] = {}
                        sim_user[user_list[index_s]][user_list[index_f]] = sim_user[user_list[index_f]][
                            user_list[index_s]]
        # print('相似计数表')
        # print(sim_user)

        # 相似度计算
        for sim_key_f, sim_value_f in sim_user.items():
            for sim_key_s, sim_value_s in sim_value_f.items():
                # 假如A喜欢[1,2,3],B喜欢[1，3，4]，那么A和B的相似度为 2/sqrt(3*3)，2为相同元素的个数，3为A和B各自喜欢的总数
                sim_user[sim_key_f][sim_key_s] = sim_user[sim_key_f][sim_key_s] / sqrt(
                    len(user_item[sim_key_f]) * len(user_item[sim_key_s]))
        # print('相似分数表')
        # print(sim_user)
        return user_item, sim_user


if __name__ == '__main__':
    # Recommend('../static/data/actor_similarity_data.csv', 1314124, 6).run()
    Recommend().get_inverted()
