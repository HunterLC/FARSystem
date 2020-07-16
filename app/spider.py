import pymysql
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import math
import re
import traceback

class Spider:
    def __init__(self, actor):
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q = 0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US, en; q = 0.9, zh-CN; q = 0.8, zh; q = 0.7',
            'Connection': 'keep-alive',
            'Host': 'movie.douban.com',
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        self.actor = actor
        # 打开数据库连接
        self.db = pymysql.connect("localhost", "root", "123456", "farsystem")

        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        self.actor_id = 0
        self.proxy = '183.146.213.157:80'
        self.proxies = {
            'http': 'http://' + self.proxy,
            'https': 'https://' + self.proxy,
        }

    def get_actor_home_page_address(self):
        """
        寻找演员的豆瓣个人信息主页链接
        """
        chrome_options = Options()
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get('https://movie.douban.com/subject_search?search_text={}&cat=1002'.format(self.actor))
        # 网页内容
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.close()
        # 通过类名class查找目标,判断第一个标题是否是需要查找的对象
        if self.actor in soup.select('.title-text')[0].string:
            # print(soup.select('.title-text')[0])
            actor_address = soup.select('.title-text')[0]['href']
            print(self.actor + '首页地址为：' + actor_address)
            result = re.findall(".*celebrity/(.*)/", actor_address)
            # 记录演员的豆瓣唯一标识id
            self.actor_id = result[0]
            return actor_address

    def parse_actor_info(self, url):
        """
        解析演员基本信息
        :param url: 演员主页链接
        :return: actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace, actor_career
        """
        # headers信息设置过多会导致乱码，所以简化headers
        headers = {
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        # 演员个人主页界面响应成功
        if response.status_code == 200:
            print("演员个人主页界面响应成功")
            soup = BeautifulSoup(response.text, 'html.parser')
            # 演员姓名
            actor_c_name = soup.find_all('h1')[0].string
            print(actor_c_name)
            # 演员头像链接
            actor_img = soup.select('#headline .pic .nbg')[0]['href']
            print(actor_img)
            soup_div = soup.select('.info')[0]  # 获取演员信息的div
            pattern = r".*</span>:(.*)</li>"  # 匹配模式
            # print(soup_div)
            # 演员性别
            actor_gender = re.findall(pattern, str(soup_div.find_all('li')[0]).replace("\n", ""))[0].strip()
            print(actor_gender)
            # 演员星座
            actor_horoscope = re.findall(pattern, str(soup_div.find_all('li')[1]).replace("\n", ""))[0].strip()
            print(actor_horoscope)
            # 演员出生日期
            actor_birthday = re.findall(pattern, str(soup_div.find_all('li')[2]).replace("\n", ""))[0].strip()
            print(actor_birthday)
            # 演员出生地
            actor_birthplace = re.findall(pattern, str(soup_div.find_all('li')[3]).replace("\n", ""))[0].strip()
            print(actor_birthplace)
            # 演员职业
            actor_career = re.findall(pattern, str(soup_div.find_all('li')[4]).replace("\n", ""))[0].strip()
            print(actor_career)
            # 演员更多外文名
            # actor_e_name = re.findall(pattern, str(soup_div.find_all('li')[5]).replace("\n", ""))[0].strip()
            # print(actor_e_name)
            return actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace, actor_career
        else:
            print("演员个人主页界面响应失败，错误代码：" + str(response.status_code))

    def save_actor_info(self, actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace,
                        actor_career):
        """
        保存演员基本信息到数据库
        :param actor_c_name: 演员中文名
        :param actor_img: 演员头像
        :param actor_gender: 演员性别
        :param actor_horoscope: 演员星座
        :param actor_birthday: 演员生日
        :param actor_birthplace: 演员出生地
        :param actor_career: 演员职业
        :return:
        """
        sql = 'insert into actors(actor_id, actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace, actor_career) values(%s,"%s","%s","%s","%s","%s","%s","%s")' % (
            self.actor_id, actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace,
            actor_career)
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception:
            # 如果发生错误则回滚
            traceback.print_exc()
            self.db.rollback()

    def parse_actor_awards(self):
        """
        解析演员获奖信息
        :return:
        """
        # headers信息设置过多会导致乱码，所以简化headers
        headers = {
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        # 构造演员获奖界面链接
        url = 'https://movie.douban.com/celebrity/{}/awards/'.format(self.actor_id)
        # url = 'https://movie.douban.com/celebrity/1340022/awards/'
        try:
            response = requests.get(url, headers=headers)
            # 演员个人主页界面响应成功
            if response.status_code == 200:
                print("演员个人获奖界面响应成功")
                soup = BeautifulSoup(response.text, 'html.parser')
                # 演员获奖信息列表
                award_list = []
                for award_div in soup.select('.awards'):
                    # 获奖年份
                    award_year = award_div.find('h2').string
                    print(str(award_year))
                    # 详细获奖信息奖项
                    for award_ul in award_div.select('.award'):
                        # 获奖信息字典
                        award_info = {}
                        award_info['award_year'] = award_year
                        # 获奖举办典礼名
                        award_ceremony = award_ul.select('li')[0].select('a')[0].string
                        award_info['award_ceremony'] = award_ceremony
                        print(award_ceremony)
                        # 获奖头衔
                        award_name = award_ul.select('li')[1].string
                        award_info['award_name'] = award_name
                        print(award_name)
                        # 获奖所属电影，可能为空
                        award_film = ''
                        if award_ul.select('li')[2].select('a'):  # 电影有详细信息
                            award_film = award_ul.select('li')[2].select('a')[0].string
                        else:  # 电影没有详细信息或不是因为电影而获奖，例如易烊千玺2019年的奖项
                            award_film = award_ul.select('li')[2].string
                        award_info['award_film'] = award_film
                        print(award_film)
                        award_list.append(award_info)
                return award_list
            else:
                print('演员个人获奖界面响应失败:')
        except RequestException as e:
            print('获取奖项失败:' + str(e))

    def save_actor_awards(self, award_list):
        """
        保存演员获奖信息到数据库
        :param award_list: 获奖信息列表,每个item为一个字典:award_year, award_ceremony, award_name, award_film
        :return:
        """
        for award in award_list:
            if award['award_film'] != None:  # 获奖存在电影信息
                sql = "insert into awards(actor_id, award_year, award_ceremony, award_name, award_film) values(%s,'%s','%s','%s','%s')" % (
                    self.actor_id, award['award_year'], award['award_ceremony'], award['award_name'],
                    award['award_film'])
            else:  # 获奖不存在电影信息
                sql = "insert into awards(actor_id, award_year, award_ceremony, award_name) values(%s,'%s','%s','%s')" % (
                    self.actor_id, award['award_year'], award['award_ceremony'], award['award_name'])
            try:
                # 执行sql语句
                self.cursor.execute(sql)
                # 提交到数据库执行
                self.db.commit()
            except Exception:
                # 如果发生错误则回滚
                traceback.print_exc()
                self.db.rollback()

    def get_actor_films_address(self):
        """
        根据当前演员的信息获取其主演的所有电影的链接
        :return:
        """
        # headers信息设置过多会导致乱码，所以简化headers
        headers = {
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        # 构造演员参演的电影的第一页链接，获取电影总的数目
        url_first_page = 'https://movie.douban.com/celebrity/{}/movies?start=0&format=pic&sortby=time&'.format(
            self.actor_id)
        try:
            response = requests.get(url_first_page, headers=headers)
            if response.status_code == 200:
                total_film = BeautifulSoup(response.text, 'html.parser').select('#content h1')[0].string
                num = re.findall(r"[（](.*?)[）]", total_film)
                # 向上取整
                total_page = math.ceil(int(num[0]) / 10)
                # 分别获取每一页的电影详细信息链接
                film_address_list = []
                for page in range(total_page):
                    print("正在获取{}的电影链接,第{}页".format(self.actor, page + 1))
                    try:
                        # 构造链接
                        url = 'https://movie.douban.com/celebrity/{}/movies?start={}&format=pic&sortby=time&'.format(
                            self.actor_id, 10 * page)
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # 获取该页10个电影的链接
                            for href in soup.select('.nbg'):
                                film_address_list.append(href['href'])
                    except RequestException as e:
                        print("获取电影信息出错：" + str(e))
                return film_address_list
        except RequestException as e:
            print("获取电影信息出错：" + str(e))

    def parse_film_info(self, film_address_list):
        """
        解析电影基本信息
        :param film_address_list: 电影信息界面的链接列表
        :return: film_info_list 电影信息解析结果
        """
        # headers信息设置过多会导致乱码，所以简化headers
        headers = {
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        # 电影信息列表
        film_info_list = []
        for address in film_address_list:
            try:
                response = requests.get(address, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # 电影信息字典
                    film_info_dic = {}
                    # 电影id
                    film_id = re.findall(".*subject/(.*)/", address)[0]
                    film_info_dic['film_id'] = film_id
                    print('电影id：{}'.format(film_id))
                    # 主演名单
                    film_protagonist = ''
                    for actor in soup.select('.actor .attrs a'):
                        film_protagonist += actor.get_text() + " "
                    film_info_dic['film_protagonist'] = film_protagonist
                    print('主演名单：{}'.format(film_protagonist))
                    # 当前爬取的演员是主演，且该电影的评分存在才进行信息解析
                    if self.actor in film_protagonist and soup.select('strong[property="v:average"]')[0].string != None:
                        # 电影名称
                        film_name = soup.select('#content h1 span')[0].string
                        film_info_dic['film_name'] = film_name
                        print('电影名称：{}'.format(film_name))
                        # 电影出品年份
                        film_year = re.findall(r'\d+', soup.select('#content h1 span')[1].string)[0]
                        film_info_dic['film_year'] = film_year
                        print('电影出品年份：{}'.format(film_year))
                        # 电影图片
                        film_img = soup.select('.nbgnbg img')[0]['src']
                        film_info_dic['film_img'] = film_img
                        print('电影图片：{}'.format(film_img))
                        # 电影导演
                        film_director = ''
                        for director in soup.select('a[rel="v:directedBy"]'):
                            film_director += director.get_text() + " "
                        film_info_dic['film_director'] = film_director
                        print('电影导演：{}'.format(film_director))
                        # 电影类型
                        film_type = ''
                        for type in soup.select('span[property="v:genre"]'):
                            film_type += type.get_text() + " "
                        film_info_dic['film_type'] = film_type
                        print('电影类型：{}'.format(film_type))
                        # 电影地区
                        if (soup.select('#info .pl')[3].string in "制片国家/地区:"):
                            film_region = soup.select('#info .pl')[3].next_element.next_element.strip()
                        else:
                            film_region = soup.select('#info .pl')[4].next_element.next_element.strip()
                        film_info_dic['film_region'] = film_region
                        print('电影地区：{}'.format(film_region))
                        # 电影评分
                        film_score = soup.find_all('strong', property="v:average")[0].string
                        film_info_dic['film_score'] = film_score
                        print('电影评分：{}'.format(film_score))
                        # 电影评分人数
                        film_comments_sum = soup.find_all('span', property="v:votes")[0].string
                        film_info_dic['film_comments_sum'] = film_comments_sum
                        print('电影评分人数：{}'.format(film_comments_sum))
                        # 定位到电影星级评论的div
                        soup_star_div = soup.find('div',class_='ratings-on-weight')
                        # 五星率
                        film_star_ratio_five = soup_star_div.find_all('div')[0].find(class_='rating_per').string
                        film_info_dic['film_star_ratio_five'] = film_star_ratio_five
                        print('五星率：{}'.format(film_star_ratio_five))
                        # 四星率
                        film_star_ratio_four = soup_star_div.find_all('div')[2].find(class_='rating_per').string
                        film_info_dic['film_star_ratio_four'] = film_star_ratio_four
                        print('四星率：{}'.format(film_star_ratio_four))
                        # 三星率
                        film_star_ratio_three = soup_star_div.find_all('div')[4].find(class_='rating_per').string
                        film_info_dic['film_star_ratio_three'] = film_star_ratio_three
                        print('三星率：{}'.format(film_star_ratio_three))
                        # 两星率
                        film_star_ratio_two = soup_star_div.find_all('div')[6].find(class_='rating_per').string
                        film_info_dic['film_star_ratio_two'] = film_star_ratio_two
                        print('两星率：{}'.format(film_star_ratio_two))
                        # 一星率
                        film_star_ratio_one = soup_star_div.find_all('div')[8].find(class_='rating_per').string
                        film_info_dic['film_star_ratio_one'] = film_star_ratio_one
                        print('一星率：{}'.format(film_star_ratio_one))
                        film_info_list.append(film_info_dic)
                    else:
                        print("该电影暂无评分或者当前演员不是主演")
            except RequestException as e:
                print("获取电影信息出错：" + str(e))
            except IndexError:
                pass
        return film_info_list

    def save_film_info(self, film_info_list):
        """
        保存电影信息到数据库中
        :param film_info_list:
        :return:
        """
        for film in film_info_list:
            sql = "insert into films(actor_id, film_id, film_name, film_year, film_img, film_director, film_protagonist, film_type, film_region, film_score, film_comments_sum, film_star_ratio_five, film_star_ratio_four, film_star_ratio_three, film_star_ratio_two, film_star_ratio_one) values(%s,%s,'%s','%s','%s','%s','%s','%s','%s',%s,%s,'%s','%s','%s','%s','%s')" % (
                self.actor_id, film['film_id'], film['film_name'], film['film_year'], film['film_img'], film['film_director'],film['film_protagonist'], film['film_type'], film['film_region'], film['film_score'], film['film_comments_sum'], film['film_star_ratio_five'], film['film_star_ratio_four'], film['film_star_ratio_three'], film['film_star_ratio_two'], film['film_star_ratio_one'])
            try:
                # 执行sql语句
                self.cursor.execute(sql)
                # 提交到数据库执行
                self.db.commit()
            except:
                # 如果发生错误则回滚
                traceback.print_exc()
                self.db.rollback()


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
        self.db.close()


if __name__ == '__main__':
    # 电影演员名单列表，男女各10位，年龄阶段分别为20+、30+、40+
    actor_name_list = ['杨紫', '周冬雨', '关晓彤', '迪丽热巴', '杨幂', '刘诗诗', '范冰冰', '海清', '赵薇', '章子怡',
                       '吴磊', '张一山', '刘昊然', '易烊千玺', '黄轩', '王宝强', '彭于晏', '刘烨', '吴京', '黄晓明']
    for actor in actor_name_list:
        Spider(actor).run_task()
