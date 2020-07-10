import pymysql
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import math
import json
import csv
import re
import os
import traceback
import time


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
        self.count = 0  # 记录成功爬取的条数
        self.actor = actor
        # 打开数据库连接
        self.db = pymysql.connect("localhost", "root", "123456", "db7")

        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        self.actor_id = 0
        self.allscore = 0
        self.allnumber = 0
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
                sql = "insert into awards(actor_id, award_year, award_ceremony, award_name, award_film) values(%s,'%s','%s','%s','%s')"%(self.actor_id,award['award_year'],award['award_ceremony'],award['award_name'],award['award_film'])
            else:  # 获奖不存在电影信息
                sql = "insert into awards(actor_id, award_year, award_ceremony, award_name) values(%s,'%s','%s','%s')"%(self.actor_id,award['award_year'],award['award_ceremony'],award['award_name'])
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
        # headers信息设置过多会导致乱码，所以简化headers
        headers = {
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        # 构造演员参演的电影的第一页链接，获取电影总的数目
        url_first_page = 'https://movie.douban.com/celebrity/{}/movies?start=0&format=pic&sortby=time&'.format(self.actor_id)
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
                    try:
                        # 构造链接
                        url = 'https://movie.douban.com/celebrity/{}/movies?start={}&format=pic&sortby=time&'.format(
                            self.actor_id, 10 * page)
                        response = requests.get(url_first_page, headers=headers)
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
        # headers信息设置过多会导致乱码，所以简化headers
        headers = {
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        for address in film_address_list:
            try:
                response = requests.get(address, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
            except RequestException as e:
                print("获取电影信息出错：" + str(e))
        return

    def save_film_info(self, film_list):
        return


    def run_task(self):
        # 获取演员主页链接
        actor_address = self.get_actor_home_page_address()
        # # 解析演员基本信息
        # actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace, actor_career = self.parse_actor_info(actor_address)
        # # 存储演员基本信息到数据库
        # self.save_actor_info(actor_c_name, actor_img, actor_gender, actor_horoscope, actor_birthday, actor_birthplace,
        #                 actor_career)
        # # 获取演员获奖信息
        # award_list = self.parse_actor_awards()
        # # 保存演员获奖信息到数据库
        # self.save_actor_awards(award_list)
        # 获取演员参演的电影信息
        film_address_list = self.get_actor_films_address()
        print(film_address_list)
        # film_info_list = self.parse_film_info(film_address_list)
        # # 保存演员获奖信息到数据库
        # self.save_film_info(film_info_list)
        self.db.close()


if __name__ == '__main__':

    list = ['张子枫']
    # list = ['杨紫', '关晓彤', '孙俪', '杨幂', '范冰冰', '袁泉', '郝蕾', '赵薇', '李冰冰', '刘昊然', '吴磊', '张一山', '胡歌', '彭于晏', '邓超', '吴京', '古天乐',
    #  '夏雨', '周星驰']
    for l in list:
        l1 = Spider(l)
        l1.run_task()
