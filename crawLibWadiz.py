import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import os
from selenium import webdriver
import time
from urllib.request import urlopen
from lxml import etree
import pymysql
from datetime import datetime
import re
##########Wadiz crawling############
#####Wadiz Reward 카테고리별 크롤링하기

#wadiz reward 페이지
###popup control###
class WadizCrawler:
    def __init__(self):
        self.conn = pymysql.connect(host='106.246.169.202', user='root', password='robot369',
                               db='crawl', charset='utf8mb4')

        self.path = os.path.dirname(os.path.realpath(__file__))

    def extractCol(self,tree, category, title, brand,achieve, funding, supporter, likes, goal, period, remaining):

        try:
            category = category[0]
        except:
            category = 'None'
        try:
            title = title[0]
        except:
            title = 'None'
        try:
            brand = brand[0]
        except:
            brand = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[3]/div/div[1]/dl/dd/p/a/text()')
            try:
                brand = brand[0]
            except:
                brand = 'None'
        try:
            achieve = achieve[0]
        except:
            achieve = 'None'
        try:
            supporter = supporter[0]
        except:
            supporter = 'None'
        try:
            likes = likes[0]
        except:
            likes = 'None'
        try:
            funding = funding[0]
        except:
            likes = 'None'
        try:
            goal = goal[0].strip()
        except:
            goal = 'None'
        try:
            period = period[0].strip()
        except:
            period = 'None'
        try:
            remaining = remaining[0]
        except:
            remaining = 'None'
        try:
            stdate = period.split('-')[0].replace('.', '-')
        except:
            stdate = 'None'
        try:
            endate = period.split('-')[1].replace('.', '-')
        except:
            endate = 'None'
        return category, title, brand,achieve, funding, supporter, likes, goal, period, remaining, stdate, endate
    def cleansing(self, text):
        try:
            text = re.sub('[ㅣ,#/:$@*\"※&%ㆍ』\\‘|\(\)\[\]\<\>`\'…》]', '', text)

            text = re.sub(r'\\', '', text)
            text = re.sub(r'\\\\', '', text)
            text = re.sub('\'', '', text)
            text = re.sub('\"', '', text)

            text = re.sub('\u200b', ' ', text)
            text = re.sub('&nbsp;|\t', ' ', text)
            text = re.sub('\r\n', '\n', text)

            while (True):
                text = re.sub('  ', ' ', text)
                if text.count('  ') == 0:
                    break

            while (True):
                text = re.sub('\n \n ', '\n', text)
                # print(text.count('\n \n '))
                if text.count('\n \n ') == 0:
                    break

            while (True):
                text = re.sub(' \n', '\n', text)
                if text.count(' \n') == 0:
                    break

            while (True):
                text = re.sub('\n ', '\n', text)
                if text.count('\n ') == 0:
                    break

            while (True):
                text = re.sub('\n\n', '\n', text)
                # print(text.count('\n\n'))
                if text.count('\n\n') == 0:
                    break
            text = re.sub(u'[\u2500-\u2BEF]', '', text)  # I changed this to exclude chinese char

            # dingbats
            text = re.sub('\\-|\]|\{|\}|\(|\)', "", text)

            text = re.sub(u'[\u2702-\u27b0]', '', text)
            text = re.sub(u'[\uD800-\uDFFF]', '', text)
            text = re.sub(u'[\U0001F600-\U0001F64F]', '', text)  # emoticons
            text = re.sub(u'[\U0001F300-\U0001F5FF]', '', text)  # symbols & pictographs
            text = re.sub(u'[\U0001F680-\U0001F6FF]', '', text)  # transport & map symbols
            text = re.sub(u'[\U0001F1E0-\U0001F1FF]', '', text)  # flags (iOS)
        except Exception as e:
            print('cleaser error')
            text = 'None'
        return text

    def getUrlLister(self, pagename, page_url, nUrl):
        option = Options()

        option.add_argument("--disable-infobars")
        option.add_argument("start-maximized")
        option.add_argument("--disable-extensions")

        # Pass the argument 1 to allow and 2 to block
        option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
        })
        driver = webdriver.Chrome(options=option, executable_path=self.path + "\chromedriver.exe")
        driver.get(page_url)

        conn = self.conn
        curs = conn.cursor()

        n_scrollDown = nUrl//48 + 2
        k=0
        while k<n_scrollDown+1:
            k+=1
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            print(str(k)+"번 반복했습니다.")

        for i in range(1, nUrl+1):
            xpath ='/html/body/div[1]/main/div[2]/div/div[3]/div[2]/div[1]/div[%s]/div/a'%(i)
            url = driver.find_element_by_xpath(xpath)
            url = url.get_attribute('href')
            sql0 = "select * from wadiz_urllist where url=\'%s\'" % (url)
            curs.execute(sql0)
            rows = curs.fetchall()
            status = 'F'
            if len(rows)==0:
                sql= "insert into wadiz_urllist(url, pagename, crawled) values (\'%s\',\'%s\',\'%s\')"%(url, pagename,status)
                curs.execute(sql)
                conn.commit()

            print(i,url)
            #url = url.get_attribute('href')
            #print(url)
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        conn.close()

    def getCrawler(self):
        conn = self.conn
        curs = conn.cursor()
        #크롤링 안된 url 가져오기
        sql = "select * from wadiz_urllist where crawled='F' or crawled='DB insert error'"
        curs.execute(sql)
        rows = curs.fetchall()
        #크롤링이 안된 모든 행들에 대해서 실시
        for row in rows:

            # id, pagename, url 을 urllist 에서 가져온다
            id = row[0]
            pagename = row[1]
            url = row[2]
            # 해당 url 을 이용해서 requests 하고 요소들을 가져온다.
            response = urlopen(url)
            htmlparser = etree.HTMLParser()
            tree = etree.parse(response, htmlparser)

            category = tree.xpath('//*[@id="container"]/div[2]/p/em/text()')
            title = tree.xpath('//*[@id="container"]/div[2]/h2/a/text()')
            brand = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[4]/div/div[1]/dl/dd/p/a/text()')
            achieve = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[3]/strong/text()')
            funding = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[4]/strong/text()')
            supporter = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[5]/strong/text()')
            likes = tree.xpath('//*[@id="cntLike"]/text()')
            goal = tree.xpath(
                '//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[3]/div/p[1]/text()[1]')

            period = tree.xpath(
                '//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[3]/div/p[1]/text()[2]')
            remaining = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[1]/text()')
            try:
                if remaining[0] == '% 달성':
                    funding = tree.xpath(
                        '//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[2]/strong/text()')
                    supporter = tree.xpath(
                        '//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[3]/strong/text()')
                    likes = tree.xpath('//*[@id="cntLike"]/text()')
            except:
                print('url:',url)
            now = datetime.now()
            dtStr = now.strftime("%Y-%m-%d %H:%M:%S")

            category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate = self.extractCol(tree, category, title, brand,achieve, funding, supporter, likes, goal, period, remaining)

            category = self.cleansing(category)
            title = self.cleansing(title)
            brand = self.cleansing(brand)
            achieve = self.cleansing(achieve)
            funding = self.cleansing(funding)
            supporter = self.cleansing(supporter)
            likes = self.cleansing(likes)
            goal = self.cleansing(goal)
            period = self.cleansing(period)
            remaining = self.cleansing(remaining)
            nowday = now.strftime("%Y-%m-%d")

                # sql3 = "update wadiz_urllist set crawled='DB insert Error' where url=\'%s\'" % (url)
                # curs.execute(sql3)
                # conn.commit()
                # print('first', id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate, dtStr, url)
            # url 을 통해 가져온 내용들을 crawl 테이블에 저장한다.
            # id 를 통해
            sql0 = "select count(*) from wadiz_crawl where id = %d and remaining=\'%s\'"% (id, remaining)
            curs.execute(sql0)
            row = curs.fetchall()
            if row[0][0]==0:
                try:
                    if endate>=nowday:
                        sql1 = 'insert into wadiz_crawl (id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate, accesstime)\
                                                value(%d,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')'\
                                                    %(id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate, dtStr)
                        curs.execute(sql1)
                        conn.commit()
                        print('Crawling '+url+' finish',sql1)

                        conn.commit()
                    elif remaining=='펀딩성공':
                        sql1 = 'insert into wadiz_crawl (id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate, accesstime)\
                                                                        value(%d,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' \
                               % (
                               id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period,
                               remaining, stdate, endate, dtStr)
                        curs.execute(sql1)
                        conn.commit()
                        print('Crawling ' + url + ' finish', sql1)

                        sql = "update wadiz_urllist set crawled='T' where url=\'%s\'" % (url)
                        curs.execute(sql)
                        conn.commit()
                    else:
                        remaining='펀딩실패'
                        sql1 = 'insert into wadiz_crawl (id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate, accesstime)\
                                                                        value(%d,\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' \
                               % (
                               id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period,
                               remaining, stdate, endate, dtStr)
                        curs.execute(sql1)
                        conn.commit()
                        print('Crawling ' + url + ' finish', sql1)

                        sql = "update wadiz_urllist set crawled='T' where url=\'%s\'" % (url)
                        curs.execute(sql)
                        conn.commit()
                except:
                    sql0 = "update wadiz_urllist set crawled='DB insert Error' where url=\'%s\'"%(url)
                    curs.execute(sql0)
                    conn.commit()
                    print('second',sql0, url)
        else:
            print(url+"already exist")
        conn.close()
