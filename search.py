#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import requests
import random
import re
import html_str_util
from pool import Pool
from bs4 import BeautifulSoup


#global variabal
search_url = 'https://www.xbiquge6.com/search.php'

#search fiction in https://www.xbiquge6.com/search.php
def search(filter):
    html = get_html(search_url+'?keyword='+filter)
    bs = BeautifulSoup(html, 'lxml')
    divs = bs.find_all('div', class_ = 'result-item')
    for div in divs:
        get_item(div)
        for child in div.descendants:
            if child.name == 'img':

            print(child)
def get_item(item):
    item_str = '' 
    for child in item.descendants:
        if child.name == 'img':
            item_str = item_str+'\"image\":'+child.get('src')+','
        if child.name == 'a':
            item_str = item_str+'\"url\":' + child.get('href')+','

#get html string
def get_html(url):
    pool = Pool()
    proxies = pool.pool()
    keys = list(proxies.keys())
    proxy = keys[random.randrange(0, len(keys))]
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    while True:
        try:
            req=requests.get(url,headers=headers, proxies = proxies[proxy], timeout=5)
            req.encoding='UTF-8'
            return html_str_util.filter_tags(req.text) 
        except requests.exceptions.RequestException:
            pass

if __name__ == '__main__':
    search(sys.argv[1])
