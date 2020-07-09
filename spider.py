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
    def __init__(self,actor):
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q = 0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US, en; q = 0.9, zh-CN; q = 0.8, zh; q = 0.7',
            'Connection': 'keep-alive',
            'Host': 'movie.douban.com',
            'Referer': 'https://movie.douban.com/celebrity/1048026/movies?start=10&format=pic&sortby=time&role=A1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        self.count = 0 # 记录成功爬取的条数
        self.actor=actor
        # 打开数据库连接
        self.db = pymysql.connect("localhost", "root", "123456", "farsystem")

        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()
        self.aid=0
        self.allscore=0
        self.allnumber=0
        self.proxy='183.146.213.157:80'
        self.proxies = {
                        'http': 'http://' + self.proxy,
                        'https': 'https://' + self.proxy,
        }

    def get_actor_home_page_address(self):
        """
        寻找演员的豆瓣个人信息主页链接
        :return 演员主页链接actor_address
        """
        chrome_options = Options()
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get('https://movie.douban.com/subject_search?search_text={}&cat=1002'.format(self.actor))
        # 网页内容
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.close()
        #通过类名class查找目标,判断第一个标题是否是需要查找的对象
        if self.actor in soup.select('.title-text')[0].string:
            print(soup.select('.title-text')[0])
            actor_address = soup.select('.title-text')[0]['href']
            print(self.actor+'首页地址为：'+ actor_address)
            self.parse_actor(actor_address)

    def parse_actor(self, url):
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
            result = re.findall(".*celebrity/(.*)/", url)
            # 记录演员的豆瓣唯一标识id
            self.aid = result[0]
            # 演员姓名
            actor_c_name = soup.find_all('h1')[0].string
            print(actor_c_name)
            soup_div = soup.select('.info')
            print(soup_div[0])
            # 演员性别
            actor_gender = soup.find_all('h1')[0].string
            print(actor_gender)
            # 演员星座
            actor_horoscope = soup.find_all('h1')[0].string
            print(actor_horoscope)
            # 演员出生日期
            actor_birthday = soup.find_all('h1')[0].string
            print(actor_birthday)
            # 演员出生地
            actor_birthplace = soup.find_all('h1')[0].string
            print(actor_birthplace)
            # 演员职业
            actor_career = soup.find_all('h1')[0].string
            print(actor_career)
            # 演员更多外文名
            actor_e_name = soup.find_all('h1')[0].string
            print(actor_e_name)
            # 演员家庭成员
            actor_folks = soup.find_all('h1')[0].string
            print(actor_folks)
            # self.save_actorinfo(soup)
        else:
            print("演员个人主页界面响应失败，错误代码：" + str(response.status_code))

    def save_actorinfo(self, soup):

        p = r".*</span>:(.*)</li>"
        # name = soup.select('#content h1')[0].string
        # print(name)
        # sex = re.findall(p, str(soup.select('.info ul li')[0]).replace("\n", ""))
        # star = re.findall(p, str(soup.select('.info ul li')[1]).replace("\n", ""))
        # birthday = re.findall(p, str(soup.select('.info ul li')[2]).replace("\n", ""))
        # birthplace = re.findall(p, str(soup.select('.info ul li')[3]).replace("\n", ""))
        # img = soup.select('#headline .pic .nbg')[0]['href']
        # print(sex[0].strip())
        # print(star[0].strip())
        # print(birthday[0].strip())
        # print(birthplace[0].strip())
        # print(img)
        # img_name = img.split('/')[-1]
        # img_path = 'app\\static\\images\\{}'.format(img_name)
        # print(os.getcwd())
        # print(img_path)
        # try:
        #     if not os.path.exists(img_path):
        #
        #         r = requests.get(img)
        #
        #         with open(img_path, 'wb') as f:
        #             f.write(r.content)
        #             f.close()
        #             print("文件保存成功")
        #     else:
        #         print("文件已存在")
        # except Exception as err:
        #     print(err)
        # sql = 'insert into actors(`aid`,`name`,`sex`,`star`,`birthday`,`birthplace`,`img`) values(%s,"%s","%s","%s","%s","%s","%s")' % (
        #     self.aid, name, sex[0].strip(), star[0].strip(), birthday[0].strip(), birthplace[0].strip(), img_name)
        # try:
        #     # 执行sql语句
        #     self.cursor.execute(sql)
        #     # 提交到数据库执行
        #     self.db.commit()
        # except Exception:
        #     # 如果发生错误则回滚
        #     traceback.print_exc()
        #     self.db.rollback()

    def run(self):
        self.get_actor_home_page_address()
        self.db.close()


if __name__ == '__main__':

    list = ['张子枫']
    for l in list:
        l1 = Spider(l)
        l1.run()