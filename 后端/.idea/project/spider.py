import requests
import csv
import time
import json
import re
import csv
import tensorflow as tf
import jieba
import re
import os
import queue
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from gensim.models import KeyedVectors
import threadpool
import threading
from bs4 import BeautifulSoup
from lxml import etree
lock=threading.Lock() #申请一把锁
stopWordsPath = "D:/IDEA_workspace/NLPStudy01/.idea/source/stopword02.txt"
def mkdir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print('Directory create successfully!')
        return True
    else:
        print('Directory already exists!')
        return False
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords

def cutsentences(sentences, filepath):     #定义函数实现分词
    cutsentence = jieba.lcut(sentences.strip())     #精确模式
    stopwords = stopwordslist(filepath)     # 这里加载停用词的路径
    lastsentences = ''
    for word in cutsentence:     #for循环遍历分词后的每个词语
        if word not in stopwords:     #判断分词后的词语是否在停用词表内
            if word != '\t':
                lastsentences += word
    return lastsentences
def filter_tags(html):
    soup = BeautifulSoup(html,'html.parser')
    return soup.get_text()
def clean(text):
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
    # text = re.sub(r"#\S+#", "", text)      # 保留话题内容
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)       # 去除网址
    text = text.replace("转发微博", "")       # 去除无意义的词语
    text = text.replace("Repost", "")       # 去除无意义的词语
    text = re.sub(r"\s+", " ", text) # 合并正文中过多的空格

    return text.strip()
def get_html(url,second):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
        'X-Requested-With': 'XMLHttpRequest'
    }
    cookies = {
        'cookie': '_T_WM=cebd0c12748a76a18be0b2402f204aaa; SCF=Anb0PhuPVF5RdTp68d4grf7JfOp2exXDlSTsEsddYJlpJOTCm_hAoZIt0ZEBVebubLYJPV-WojDfDcGW-6G5UyM.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFR8mw5yj672xmsql2o2AUq5NHD95QNSh2XeoMXeh5EWs4Dqcje-cH_MsHEHJLoUGH0; SUB=_2A25PvIr5DeRhGeFK6lYT9yrMyz6IHXVtXhaxrDV6PUJbktCOLU2ikW1NQ5vC7FZ1_9bLaeMKjgjKq8Ut9-FrhcWc; ALF=1658881961; WEIBOCN_FROM=1110006030; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D2304137420121935_-_WEIBO_SECOND_PROFILE_WEIBO%26fid%3D2304137420121935_-_WEIBO_SECOND_PROFILE_WEIBO%26uicode%3D10000011; XSRF-TOKEN=ef3a61; mweibo_short_token=1c2b0d6444'
    }
    response = requests.get(url, headers=headers, cookies=cookies)
    time.sleep(second)   # 加上3s 的延时防止被反爬
    return response.text


def save_data(data,uid):
        title = ['created_at', 'text']
        test=['M','T','F','S']
        if(data['created_at'][0][0:1] not in test):
            return
        with open("D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv", "a", encoding="utf-8", newline="", errors='ignore')as fi:
            fi = csv.writer(fi)
            fi.writerow([data[i] for i in title])
def convert(time):
    list=time.split()
    res=''
    for i in [0,1,2,3,5]:
        if(i!=5):
            res+=list[i]+" "
        else:
            res+=list[i]
    return res
def get_pages(uid):
    pages=[]
    head = "https://m.weibo.cn/api/container/getIndex?containerid=230413"
    last = "_-_WEIBO_SECOND_PROFILE_WEIBO"
    url = head+str(uid)+last
    html = get_html(url,0.5)
    responses = json.loads(html)
    min_since_id=responses.get('data').get('cardlistInfo').get('since_id')
    pages.append(min_since_id);
    blogs = responses['data']['cards']
    items = responses.get('data').get('cards')
    for item in items:
        data = {}
        item = item.get('mblog')
        if(item):   # 发布时间
            final_text= cutsentences(filter_tags(clean(item.get('text'))),stopWordsPath)
            if len(final_text)!=0:
                data['created_at'] = convert(item.get('created_at'))
                data['text'] = final_text     # 博文正文文字数据
                save_data(data,uid)
    last = "_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03&since_id="
    while min_since_id and len(pages)<=50:
        url=head+str(uid)+last+str(min_since_id)
        html = get_html(url,0.3)
        responses = json.loads(html)
        min_since_id = responses.get('data').get('cardlistInfo').get('since_id')
        if(min_since_id):
         pages.append(min_since_id)
         print("取得sinceid:"+str(min_since_id))
    return pages
def spider_single(since_id,uid):
    url = "https://m.weibo.cn/api/container/getIndex?containerid=230413" +str(uid)+"_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03&since_id="+str(since_id)
    resp = requests.get(url)
    html = get_html(url,0.5)
    responses = json.loads(html)
    items = responses.get('data').get('cards')
    data = {}
    for item in items:
        item = item.get('mblog')
        if(item):
            final_text= cutsentences(filter_tags(clean(item.get('text'))),stopWordsPath)
            if len(final_text)!=0:
                data['created_at'] = convert(item.get('created_at'))  # 发布时间
                data['text'] = final_text      # 博文正文文字数据
                print(data)
                lock.acquire()
                save_data(data,uid)
                lock.release()
def spider(uid):
    pages=get_pages(uid)
    data = [(None,{'uid':uid,'since_id':i}) for i in pages ]
    pool = threadpool.ThreadPool(20)
    tasks = threadpool.makeRequests(spider_single, data)
    #makeRequests构造线程task请求,第一个参数是线程函数,第二个是参数数组
    [pool.putRequest(task) for task in tasks]
    #列表推导式,putRequest向线程池里加task,让pool自己去调度task
    pool.wait() #等所有任务结束

if __name__ == '__main__':
    spider(7089246227)