# -*- coding: UTF-8 -*-
import re
import os
import requests
import urllib
import time
from bs4 import BeautifulSoup

        
class WenShu:
    def __init__(self):
        self.index = 1
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36'
        self.headers = {'User-Agent':self.user_agent }
        self.search_criteria = ''
        self.download_conditions = ''
        self.item_in_page = '20'
        self.total_items = ''
        self.case = {}
        self.search_url = 'http://wenshu.court.gov.cn/List/ListContent'
        self.download_url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateListDocZip.aspx?action=1'
        self.data = {'Param':self.search_criteria,\
                     'Index': self.index,\
                     'Page':self.item_in_page,\
                     'Order':'法院层级',\
                     'Direction':'asc'}


    def setSearchCriteria(self, search_criteria):
        self.search_criteria = search_criteria
        self.data = {'Param':self.search_criteria,\
                     'Index': self.index,\
                     'Page':self.item_in_page,\
                     'Order':'法院层级',\
                     'Direction':'asc'}


    def setDownloadConditions(self):
        self.download_conditions = self.search_criteria.replace(':', '为').replace(',', '且')


    def getContent(self, maxPage):
        for index in range(1, maxPage+1):
            print("Page %s" % index)
            self.LoadPageContent(index)
            self.downloadDocument()
            p = [self.date, self.case_id, self.title, self.doc_id, self.brief, self.procedure, self.court]
            with open('results.csv', 'a') as f:
                f.write(codecs.BOM_UTF8)
                writer = csv.writer(f)
                for item in zip(*p):
                    writer.writerow(item)

                    
    def downloadDocument(self, name, id, date):
        docIds = id + '|' + name + '|' + date
        condition = urllib.parse.quote(self.download_conditions)
        data = {'conditions':condition,'docIds':docIds,'keyCode':''}
        r = requests.post(self.download_url, headers = self.headers, data = data)
       
        if r.status_code != 200: 
            print(r.status_code)
        else:
            print("Downloading case %s"%(name))
            with open('Download/' + name + date + ".docx", "wb") as word_doc:
                word_doc.write(r.content)
            
    def getTotalItemNumber(self):
        r = requests.post(self.search_url, headers=self.headers, data=self.data)
        raw = r.json()
        if raw == 'remind':
            self.handleValidateCode()
            # re-send requests
            r = requests.post(self.search_url, headers=self.headers, data=self.data)
            raw = r.json()
        pattern = re.compile('"Count":"([0-9]+)"', re.S)
        total_number = re.findall(pattern, raw)
        self.total_items = int(total_number[0]) if total_number else 0
    
    def getCaseList(self, total_items):
        name_list = []
        date_list = []
        id_list = []
        max_page = (total_items // int(self.item_in_page)) + 1
        for index in range(1, max_page + 1):
        #for index in range(1, 2):
            print("Get Case list on page %s" % index)
            self.data['Index'] = index
            r = requests.post(self.search_url, headers=self.headers, data=self.data)
            try:
                raw = r.json()
            except:
                print('exception catch, re-send request.')
                self.handleValidateCode()
                r = requests.post(self.search_url, headers=self.headers, data=self.data)
                raw = r.json()
            if raw == 'remind':
                self.handleValidateCode()
                # If blocked by website, hold and refresh manually, and then re-send requests
                r = requests.post(self.search_url, headers=self.headers, data=self.data)
                raw = r.json()
            pattern_name = re.compile('"案件名称":"(.*?)"', re.S)
            name_list += re.findall(pattern_name, raw)
            pattern_id = re.compile('"文书ID":"(.*?)"', re.S)
            id_list += re.findall(pattern_id, raw)
            pattern_date = re.compile('"裁判日期":"(.*?)"', re.S)
            date_list += re.findall(pattern_date,raw)
        self.case['name'] = name_list
        self.case['id'] = id_list
        self.case['date'] = date_list
    
    def getHomePage(self, url):
        res = requests.get(url)
        res.encoding = 'utf-8'
        print(res.text)
    
    def handleValidateCode(self):
        input("Refresh the Page and Enter:")
    
    
    def LoadPageContent(self, index):
        #记录开始时间
        begin_time = datetime.datetime.now()
        url = 'http://wenshu.court.gov.cn/List/ListContent'
        self.data['Index'] = index
        r = requests.post(url, headers = self.headers, data = self.data)
        raw=r.json()

        pattern1 = re.compile('"裁判日期":"(.*?)"', re.S)
        self.date = re.findall(pattern1,raw.encode("utf-8"))
        
        pattern2 = re.compile('"案号":"(.*?)"', re.S)
        self.case_id = re.findall(pattern2,raw.encode("utf-8"))
        
        pattern3 = re.compile('"案件名称":"(.*?)"', re.S)
        self.title = re.findall(pattern3,raw.encode("utf-8"))
        
        pattern4 = re.compile('"文书ID":"(.*?)"', re.S)
        self.doc_id = re.findall(pattern4,raw.encode("utf-8"))
        
        pattern5 = re.compile('"裁判要旨段原文":"(.*?)"', re.S)
        self.brief = re.findall(pattern5,raw.encode("utf-8"))
        
        pattern6 = re.compile('"审判程序":"(.*?)"', re.S)
        self.procedure = re.findall(pattern6,raw.encode("utf-8"))
        
        pattern7 = re.compile('"法院名称":"(.*?)"', re.S)
        self.court = re.findall(pattern7,raw.encode("utf-8"))

