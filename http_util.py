# -*- coding: utf-8 -*-
#!/usr/bin/python3
#@author xuan
#@created 2019/10/23
#@desciption some utils for this project 

#system lib
import requests

#my lib
import html_str_util

#get html string
def get_html(url,proxies):
    proxies =proxies 
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
    while True:
        try:
            req=requests.get(url,headers=headers, proxies = proxies, timeout=5)
            req.encoding='UTF-8'
            return html_str_util.filter_tags(req.text) 
        except requests.exceptions.RequestException:
            pass
