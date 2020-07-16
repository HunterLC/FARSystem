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
