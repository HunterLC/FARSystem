# FARSystem
An analyzer and recommender for films and actors.

# 项目阶段
## 数据收集阶段
1.采用python爬虫，利用selenium、BeautifulSoup、requests等库

2.框架结构
```
    def run_task(self):
        """
        执行工作任务
        逻辑：获取演员主页的链接 -> 爬取演员的基本信息并保存到数据库 -> 爬取演员的获奖信息并保存到数据库 -> 获取演员所参演电影的链接 -> 爬取演员参演电影的基本信息并保存到数据库
        """
        # 获取演员主页链接
        actor_address = self.get_actor_home_page_address()
        # 解析演员基本信息
        actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace, actor_career = self.parse_actor_info(actor_address)
        # 存储演员基本信息到数据库
        self.save_actor_info(actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace,
                        actor_career)
        # 获取演员获奖信息
        award_list = self.parse_actor_awards()
        # 保存演员获奖信息到数据库
        self.save_actor_awards(award_list)
        # 获取演员参演的电影链接
        film_address_list = self.get_actor_films_address()
        print(film_address_list)
        # 解析电影的基本信息
        film_info_list = self.parse_film_info(film_address_list)
        # 保存演员获奖信息到数据库
        self.save_film_info(film_info_list)
```

# 项目日志
## 2020-08-04
+ 完成演员电影类型计算
## 2020-08-03
+ 完成演员的如下特征提取
>性别、年龄段、平均电影评分、平均电影评论、获奖个数、电影部数、职业多样化、出生地、星座、平均五星率、平均四星率、平均三星率、平均两星率、平均一星率、是否国际化、电影类型总数
## 2020-09-02
+ 给学弟学妹开第三次会议，进展不错
## 2020-07-31
+ 演员推荐系统需要哪些特征?(性别、年龄段、平均电影评分、平均电影评论、获奖个数、电影部数、职业多样化、出生地、星座、平均五星率、平均四星率、平均三星率、平均两星率、平均一星率、是否国际化、电影类型总数、每种类型占比)
## 2020-07-29
+ 完善电影检索功能，存在一个BUG：搜索之后select选中了但不会显示在输入框中
+ ![电影信息之搜索电影](https://github.com/HunterLC/FARSystem/blob/master/static/image/film_search.png)
+ 设计电影详细信息界面
+ ![电影信息之详细信息](https://github.com/HunterLC/FARSystem/blob/master/static/image/film_info.png)
## 2020-07-28
+ 设计演员统计信息界面
+ ![演员信息之统计信息截图](https://github.com/HunterLC/FARSystem/blob/master/static/image/actor_info_data_statistic.png)
+ 设计演员电影信息界面
+ ![演员信息之电影列表截图](https://github.com/HunterLC/FARSystem/blob/master/static/image/actor_info_film_list.png)
+ 设计菜单栏之电影列表界面，完成分页设计和部分检索设计
## 2020-07-26
+ 开会，学弟学妹的项目需要更加细致才行
## 2020-07-22
+ 设计演员出演电影类型的饼图
## 2020-07-21
+ 设计演员个人信息界面的个人信息展示模块
+ 设计获奖时间线
+ ![演员信息之获奖时间线截图](https://github.com/HunterLC/FARSystem/blob/master/static/image/actor_info_award_timeline.png)
## 2020-07-20
+ 测试Apriori算法效果，min_support参数不宜太小，否则计算量过大
## 2020-07-19
+ 给学弟学妹答疑第一周工作任务，安排第二周工作
+ 编写部分Apriori关联挖掘算法
## 2020-07-18
+ 按照年份给出演员的获奖信息
+ web系统首页设计和详细信息界面跳转实现
+ ![首页截图](https://github.com/HunterLC/FARSystem/blob/master/static/image/start.png)
## 2020-07-17
+ 完成演员出演电影的类型分布计算
+ 完成演员出演电影的地区分布计算
+ 按照年份给出演员出演电影的类型
## 2020-07-16
1. 修改Actors表的结构，新增电影平均分数和平均评论人数
2. 利用接口完成演员的电影平均分数和平均评论人数计算和保存
3. 更新farsystem.sql文件
## 2020-07-15
1. 修改flask项目的文件框架
```
FLASK_APP = run.py
FLASK_ENV = development
FLASK_DEBUG = 1
In folder E:/PythonCode/FARSystem
E:\PythonCode\FARSystem\venv\Scripts\python.exe -m flask run
```
## 2020-07-14
+ 完成演员数据的爬取并保存到数据库
```
    # 电影演员名单列表，男女各10位，年龄阶段分别为20+、30+、40+
    actor_name_list = ['杨紫', '周冬雨', '关晓彤', '迪丽热巴', '杨幂', '刘诗诗', '范冰冰', '海清', '赵薇', '章子怡',
                       '吴磊', '张一山', '刘昊然', '易烊千玺', '黄轩', '王宝强', '彭于晏', '刘烨', '吴京', '黄晓明']
    for actor in actor_name_list:
        Spider(actor).run_task()
```
+ 将数据库转储为SQL文件（farsystem.sql）
## 2020-07-13
1. 给学弟学妹们讲项目任务分工以及第1-2周的工作内容
2. 补充电影信息之导演信息的爬取

## 2020-07-11
1. 完成电影信息解析的代码，并保存到数据库

## 2020-07-10
1. 完善演员基本信息解析的代码
2. 完成演员获奖信息的爬取
3. 完成演员基本信息和获奖信息保存到mysql数据库

## 2020-07-09
1. 爬虫代码编写，目前处于解析演员基本信息阶段
