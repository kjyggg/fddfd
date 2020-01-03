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
import pymysql

def cleansing(text):
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
    return text

now = datetime.now()

pagename = 'reward'
url = 'https://www.wadiz.kr/web/campaign/detail/46945'
response = urlopen(url)
htmlparser = etree.HTMLParser()
tree = etree.parse(response, htmlparser)

text = tree.xpath('//*[@id="introdetails"]/text()')
print(text)
category = tree.xpath('//*[@id="container"]/div[2]/p/em/text()')
title = tree.xpath('//*[@id="container"]/div[2]/h2/a/text()')
brand = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[4]/div/div[1]/dl/dd/p/a/text()')

achieve = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[1]/strong/text()')
funding = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[4]/strong/text()')
'//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[2]/strong'
'//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[4]/strong'
'//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[4]/strong'
supporter = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[5]/strong/text()')
likes = tree.xpath('//*[@id="cntLike"]/text()')
goal = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[3]/div/p[1]/text()[1]')

period = tree.xpath(
    '//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[3]/div/p[1]/text()[2]')
remaining = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[1]/div[1]/p[1]/text()')
dtStr = now.strftime("%Y-%m-%d %H:%M:%S")
nowday = now.strftime("%Y-%m-%d")
print(nowday)
print('remaining',remaining)
if remaining[0]=='% 달성':
    print('rr')
    funding = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[2]/strong/text()')
    funding = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[2]/strong/text()')
    supporter =tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[2]/div/div/section/div[4]/div/div[1]/div[1]/p[3]/strong/text()')
    likes =tree.xpath('//*[@id="cntLike"]/text()')
category = category[0]
title = title[0]
try:
    brand = brand[0]
    print(brand)
except:
    brand = tree.xpath('//*[@id="container"]/div[4]/div/div[1]/div[1]/div[3]/div/div[1]/dl/dd/p/a/text()')
    brand = brand[0]
    print('error', brand)

achieve =achieve[0]
try:
    supporter = supporter[0]
except:
    print('error')
likes = likes[0]
try:
    funding = funding[0]
except:
    print('funding')
try:
    goal = goal[0].strip()
except:
    print('funding')
period = period[0].strip()
remaining = remaining[0]
stdate = period.split('-')[0].replace('.', '-')
endate = period.split('-')[1].replace('.', '-')

category = cleansing(category)
title = cleansing(title)
brand = cleansing(brand)
achieve = cleansing(achieve)
funding = cleansing(funding)
supporter = cleansing(supporter)
likes = cleansing(likes)
goal = cleansing(goal)
period = cleansing(period)
remaining = cleansing(remaining)

print('----------------------')
print('achieve',achieve)
print(funding)
print(supporter)
print(likes)
## clease
id= 5
pagename = 'rrr'
#
# conn = pymysql.connect(host='106.246.169.202', user='root', password='robot369',
#                             db='crawl', charset='utf8mb4')
# sql1 = 'insert into wadiz_crawl (id, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate, endate, accesstime) value(%d,\'%s\', \'%s\', \'%s\', \'%s\',\'%s\', \'%s\',\'%s\', \'%s\', \'%s\', \'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' \
#        % (4189, pagename, category, title, brand, achieve, funding, supporter, likes, goal, period, remaining, stdate,
#           endate, dtStr)
# print(sql1)
# curs = conn.cursor()
# curs.execute(sql1)
# conn.commit()

