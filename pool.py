import requests
import re
from bs4 import BeautifulSoup

class Pool:
    def __init__(self):
        self.headers = { 'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

    def get_html(self,url):
        req = requests.get(url, headers = self.headers)
        req.encoding = 'UTF-8'
        return req.text




    def bs_preprocess(self,html):
        pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
        html = re.sub(pat, '', html)
        html = re.sub('\n', ' ', html)
        html = re.sub('[\s]+<', '<', html)
        html = re.sub('>[\s]+', '>', html)
        return html



    def get_pool(self,html):
        pool = {}
        bs = BeautifulSoup(html ,'lxml')
        tbody_set = bs.find_all('tbody')
        tbody = tbody_set.pop() 
        for tr in tbody.children:
            index = 0
            ip = ''
            port = ''
            for td in tr.children:
                if index == 0:
                    ip = td.get_text()
                    index = index + 1
                elif index == 1:
                    port = td.get_text()
                    break
            pool[ip]=port
        return pool

    def pool(self):   
        pool = self.get_pool(self.bs_preprocess(self.get_html('https://www.kuaidaili.com/free/inha/')))
        return pool

