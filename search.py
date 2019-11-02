#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#@author xuan
#@created 2019/10/17
#@desciption search the fiction from https://www/xbiquge6.com/search.php


#system lib
import sys
import requests
import random
import re
import pymysql
import _thread
import time
import conf
from bs4 import BeautifulSoup

#my lib
import html_str_util
from pool import Pool

#global variabal
search_url = 'https://www.xbiquge6.com/search.php?keyword='
fictions = []

#get html string
def get_html(url):
    pool = Pool()
    proxies = pool.pool()
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    while True:
        try:
            req=requests.get(url,headers=headers, proxies = proxies, timeout=5)
            req.encoding='UTF-8'
            return html_str_util.filter_tags(req.text) 
        except requests.exceptions.RequestException:
            pass
#search fiction in https://www.xbiquge6.com/search.php
def search(filter):
    html = get_html(search_url+filter)
    bs = BeautifulSoup(html, 'lxml')
    divs = bs.find_all('div', class_ = 'result-item')
    result_json = '['
    for div in divs:
        result_json = result_json + get_item(div) + ','
    result_json = result_json + ']'
    print(result_json)
    write_db(fictions)
#parse the result item,which has fiction's info
def get_item(item):
    name = ''
    image = ''
    intro = ''
    url = ''
    author = ''
    num = 0
    create_date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    updating = 0
    item_str = '{' 
    for child in item.descendants:
        if child.name == 'img':
            item_str = item_str+'\"image\":\"'+child.get('src')+'\",'
            image = child.get('src')
        if child.name == 'a' and child.has_attr('title'):
            item_str = item_str+'\"url\":\"' + child.get('href')+'\",'+'\"name\":\"'+child.get('title')+'\",'
            url = child.get('href')
            name = child.get('title')
        if child.name == 'p' and child.has_attr('class') and 'result-game-item-desc' in child['class']:
            item_str = item_str + '\"intro\":\"' + child.get_text() + '\",'
            intro = child.get_text()
        if child.name == 'p' and child.has_attr('class') and 'result-game-item-info-tag' in child['class']:
            item_str = item_str + '\"author\":\"' + trim(child.get_text()) + '\"'
            author = trim(child.get_text())
            break
    item_str = item_str + '}'
    fictions.append((name,intro,url,image,author,num,create_date,updating))
    return item_str
#create a new thread to write data
def write_db_task(fictions_list):
    try:
        _thread.start_new_thread(write_db, (fictions_list))
    except:
        print('\"status\":\"500\",\"msg\":\"new thread error\"')
#write data to database
def write_db(fictions_list):
    db = pymysql.connect(conf.mysql_host, conf.mysql_user, conf.mysql_password, conf.mysql_db)
    insert_sql = "insert into fiction(name,intro,url,image,author,num,create_date,updating) values(%s,%s,%s,%s,%s,%s,%s,%s);"
    select_sql = "select count(url) from fiction where url = %s;"
    cursor = db.cursor()
    try:
        for fiction in fictions_list:
            cursor.execute(select_sql,(pymysql.escape_string(fiction[2])))
            result = cursor.fetchone()
            if result[0] == 0:
                cursor.execute(insert_sql,(pymysql.escape_string(fiction[0]),pymysql.escape_string(fiction[1]),pymysql.escape_string(fiction[2]),pymysql.escape_string(fiction[3]),pymysql.escape_string(fiction[4]),fiction[5],pymysql.escape_string(fiction[6]),fiction[7]))
        db.commit()
    except:
        db.rollback()
        print('[\"status\":\"500\",\"msg\":\"database error\"]')
    cursor.close()
    db.close()

#去除多余的空行
def trim(string):
    string = string.replace('\n', '')
    string = string.replace('\r', '')
    string = string.strip()
    string = string.replace(' ', '')
    string = string.replace('作者：' ,'')
    return string
#start the app
if __name__ == '__main__':
    search(sys.argv[1])
