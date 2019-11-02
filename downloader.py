# -*- coding: utf-8 -*-
#!/usr/bin/python3
#@author xuan
#@created 2019/10/23
#@desciption it is a spider for getting ficiton

#system lib
import requests
import sys
import time
import json
import re
import collections
from bs4 import BeautifulSoup
import random

#my lib
import http_util
import conf

#class downloader
class downloader:
    #初始化下载器
    def __init__(self, url, num, path, fiction_id, logger, proxies):
        self.url = url #小说的地址
        self.num = num #该小说已下载的章节数
        self.path = path #该小说在磁盘的存储地址
        self.fiction_id = fiction_id #该小说在数据库中的id
        self.url_list = [] #用于存储需要更新的章节的url
        self.fic_list = collections.OrderedDict() #用于存储更新的章节的列表
        self.logger = logger
        self.proxies = proxies
    #进行下载和更新, 最后返回该小说的当前的章节数目，方便下次从该章节更新
    def update(self):
        html = http_util.get_html(self.url,self.proxies)
        bs = BeautifulSoup(html,'lxml')
        div = bs.find(id='list')
        index = 0
        #找到上次下载的该小说的章节，并从此章节开始更新
        for child in div.descendants:
            if child.name == 'a':
                if index < self.num:
                    index = index + 1
                    continue
                self.url_list.append(self.url + child.get('href').split('/')[-1])
                self.fic_list[str(index)] = str(child.get_text())
                index = index + 1
        self.write_list()
        self.download_fiction()
        return self.num
    
    #下载整本小说
    def download_fiction(self):
        currenturl = ''
        try:
            for url in self.url_list:
                time.sleep(2)
                currenturl = url 
                html = http_util.get_html(url,self.proxies)
                bs = BeautifulSoup(html, 'lxml')
                title = bs.title
                content = bs.find(id='content')
                self.write_chapter(title.get_text(),content.get_text())
                self.logger.info('fiction_id:' + str(self.fiction_id) + ':succesful when download ' + title.get_text())
        except Exception as e:
            self.logger.error('fiction_id:' + str(self.fiction_id) + ':error when downloading '+currenturl, exc_info = True)
           
    #将章节内容写到文件
    def write_chapter(self,title,content):
        chapter = collections.OrderedDict()
        chapter['title'] = title
        chapter['content'] = content
        #章节的文件名称用数字替代，即这是第几章
        with open(self.path + '/' + str(self.num) +'.json','w',encoding = 'utf-8') as f:
            json.dump(chapter, f, ensure_ascii=False)
        self.num = self.num + 1
    #把更新的小说列表写到文件
    def write_list(self):
        fiction_list = {}
        try:
            with open(self.path+'/'+'list.json','r',encoding='utf-8') as f:
                fiction_list=json.load(f, object_pairs_hook=collections.OrderedDict)
                #将上次的列表都出来和新的列表合并
                fiction_list.update(self.fic_list)
        except FileNotFoundError:
            #该小说还没有下载过，新创建列表文件
            fiction_list = self.fic_list
        #将列表写入文件
        with open(self.path+'/'+'list.json','w',encoding='utf-8') as f:
            json.dump(fiction_list, f, ensure_ascii=False)
        #记录这一次的列表更新
        self.logger.info('fiction_id:' + str(self.fiction_id) + ":write list succesful")
