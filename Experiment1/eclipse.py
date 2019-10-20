#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 19:29:14 2019

@author: novelistchan
"""

# urllib模块提供了读取Web页面数据的接口
import urllib
# re模块主要包含了正则表达式
import re
# import time
import math
# 多线程处理加快速度/添加进程锁避免对象重复操作
import threading
from bs4 import BeautifulSoup as bs

global numQ # Number of the Questions
global numW # Number of the Websites
global BF_Q # BLF for Questions
global BF_W # BLF for Websites
global BlackList # 有些外网避免访问
global WhiteList # 白名单，只有包含了这些字符的网站才访问

class myThread(threading.Thread):#线程类，用以初始化线程
    def __init__(self, threadID, name, url, depth):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.url = url
        self.depth = depth#设置深度，避免访问太多杂而无用的网页
    def run(self):
        print ('Starting' + self.name)
        GetWeb(self.url, self.depth)
        print ('Exiting' + self.name)
    
threadLock = threading.Lock()
threads = []

class BloomFilter:#布隆过滤器
    k = 0
    m = 0
    BF = [0]
    def __init__(self, n, p):
        self.m = round(-(n * math.log(p) / (math.log(2) * math.log(2))))##m = -nlnp/(ln2)^2
        self.k = round((self.m / n * math.log(2)))##k = (m/n)ln2
        self.BF = [0] * self.m ##BF扩展成m位

    def DJBHash(self, _str):
        Hash = 5381
        for i in range(len(_str)):
            Hash = ((Hash << 5) + Hash) + ord(_str[i])
        return Hash

    def insert(self, _str):
        BList = [0] * self.k
        if_insert = 0
        for i in range(self.k):
            t_str = _str + chr(i + 65)
            Hash = self.DJBHash(t_str)
            BList[i] = Hash % self.m
        for i in BList:
            if self.BF[i] == 0:
                if_insert = 1
                self.BF[i] = 1
        return if_insert

def init():#初始化信息
    global numQ
    global numW
    global BF_Q
    global BF_W
    global BlackList
    global WhiteList
    numQ = 0
    numW = 0
    BF_Q = BloomFilter(20000, 0.001)
    BF_W = BloomFilter(2000, 0.001)
    BlackList = {'amazom.com', 'google.com', '.css', 'apple.com'}
    WhiteList = {'FAQ', 'ECLIPSE'}
    return

def GetWebFAQ(url, depth):
    global numQ
    global numW
    global BlackList
    global WhiteList
    global BF_Q
    global BF_W
    
    depth = depth + 1
    if(depth > 2):
        return
        
    if BF_W.insert(url) == 0:#重复网页
        return
                    
    else:
        try:
            response = urllib.request.urlopen(url)
            print('here')
            html = response.read().decode('utf-8')
            #print('here')
            soup = bs(html, 'html.parser')
            #print(soup)
            #print('here')
            answers = soup.find_all('div', id='mw-content-text')
            #print('here')
            #answers_list = answers[0].find_all('div', class_ = 'question-summary search-result')
            #print('here')
            #print(answers[0])
            commentList = []
            for item in answers:
                if item.find_all('p')[0].string is not None:
                    commentList.append(answers[0].find_all('p')[0].string)
            print(commentList)
            if commentList != []:
                numQ = numQ + 1
            with open('/Users/novelistchan/Documents/TestGraph/eclipse.txt', 'a+') as f:
                f.write(commentList[0])
            
        except:
            return

def GetWeb(url, depth):
    global numQ
    global numW
    global BlackList
    global WhiteList
    global BF_Q
    global BF_W
    
    depth = depth + 1
    if(depth > 2):
        return
    
    visit = 0
                    
    try:
            #	request = urllib.request/Request(url)  #urllib.request.urlopen()方法用于打开一个URL地址
            #	html = response.read() #read()方法用于读取URL上的数据
            # request = urllib.request.Request(url)
            # print(request)
        response = urllib.request.urlopen(url)
            #print('here')
        html = response.read().decode('utf-8')
            #print('here')
        weblist = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')", html)         
    except:
        return

    for weburl in weblist:
        #if numQ > 200:       
        #    return
        visit = 0
        for name in WhiteList:#白名单
            if name in weburl:
                print('Visit this web')
                print(weburl)
                visit = 1
        if visit == 1:
            weburl = "https://wiki.eclipse.org" + weburl
            GetWebFAQ(weburl, depth)
    return

init()	

#创建新线程
thread1 = myThread(1, "Thread - 1", "https://wiki.eclipse.org/The_Official_Eclipse_FAQs", 0)
#thread2 = myThread(2, "Thread - 2", "http://www.sina.com.cn/", 0)
#thread3 = myThread(3, "Thread - 3", "http://www.hupu.com/", 0)

#添加线程到线程列表
threads.append(thread1)
#threads.append(thread2)
#threads.append(thread3)
#开启新线程
#等待所有线程完成
for t in threads:
    t.setDaemon(True)
    t.start()
t.join