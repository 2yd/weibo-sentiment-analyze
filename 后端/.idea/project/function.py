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


since_id = ''
stopWordsPath = "D:/IDEA_workspace/NLPStudy01/.idea/source/stopword02.txt"
savePath ="D:/IDEA_workspace/NLPStudy01/.idea/json/"
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
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata = re. compile ( '//<!\[CDATA\[[^>]*//\]\]>' ,re.I) #匹配CDATA
    re_script = re. compile ( '<\s*script[^>]*>[^<]*<\s*/\s*script\s*>' ,re.I) #Script
    re_style = re. compile ( '<\s*style[^>]*>[^<]*<\s*/\s*style\s*>' ,re.I) #style
    re_br = re. compile ( '<br\s*?/?>' ) #处理换行
    re_h = re. compile ( '</?\w+[^>]*>' ) #HTML标签
    re_comment = re. compile ( '<!--[^>]*-->' ) #HTML注释
    s = re_cdata.sub('',htmlstr) #去掉CDATA
    s = re_script.sub('',s) #去掉SCRIPT
    s = re_style.sub('',s) #去掉style
    s = re_br.sub( '' ,s) #将br转换为换行
    s = re_h.sub('',s) #去掉HTML 标签
    s = re_comment.sub('',s) #去掉HTML注释
    #去掉多余的空行
    blank_line = re. compile ( '\n+' )
    s = blank_line.sub( '\n' ,s)
    s = replaceCharEntity(s) #替换实体
    return s
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES = { 'nbsp' : ' ' , '160' : ' ' ,
                      'lt' : '<' , '60' : '<' ,
                      'gt' : '>' , '62' : '>' ,
                      'amp' : '&' , '38' : '&' ,
                      'quot' : '"','34':'"' ,}

    re_charEntity = re. compile (r'&#?(?P<name>\w+);')
    sz = re_charEntity.search(htmlstr)
    while sz:
        entity = sz.group() #entity全称，如>
        key = sz.group( 'name' ) #去除&;后entity,如>为gt
        try :
            htmlstr = re_charEntity.sub(CHAR_ENTITIES[key],htmlstr, 1 )
            sz = re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr = re_charEntity.sub('',htmlstr, 1 )
            sz = re_charEntity.search(htmlstr)
    return htmlstr
def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)
def clean(text):
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
    # text = re.sub(r"#\S+#", "", text)      # 保留话题内容
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)       # 去除网址
    text = text.replace("转发微博", "")       # 去除无意义的词语
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
    with open("D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv", "a", encoding="utf-8", newline="")as fi:
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
    while True:
        url=head+str(uid)+last+str(min_since_id)
        html = get_html(url,0.1)
        responses = json.loads(html)
        min_since_id = responses.get('data').get('cardlistInfo').get('since_id')
        if(min_since_id):
            pages.append(min_since_id)
            print("取得sinceid:"+str(min_since_id))
        else:
            break
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
                save_data(data,uid)
def spider(uid):
    pages=get_pages(uid)
    data = [(None,{'uid':uid,'since_id':i}) for i in pages ]
    pool = threadpool.ThreadPool(20)
    tasks = threadpool.makeRequests(spider_single, data)
    #makeRequests构造线程task请求,第一个参数是线程函数,第二个是参数数组
    [pool.putRequest(task) for task in tasks]
    #列表推导式,putRequest向线程池里加task,让pool自己去调度task
    pool.wait() #等所有任务结束
def predict_sentiment_catagory(text,cn_model):
    cut = jieba.cut(text)
    cut_list = [x for x in cut]
    for i, word in enumerate(cut_list):
        try:
            cut_list[i] = cn_model.key_to_index[word]
        except KeyError:
            cut_list[i] = 0
        pass
    # padding
    tokens_pad = tf.keras.preprocessing.sequence.pad_sequences([cut_list],
                                                               maxlen=int(75),
                                                               padding='pre',
                                                               truncating='pre')
    # 大于50000的归0，不归0模型的使用会报错
    tokens_pad[tokens_pad >= 50000] = 0
    return tokens_pad
def predict_sentiment_index(text,cn_model):
    cut = jieba.cut(text)
    cut_list = [x for x in cut]
    for i, word in enumerate(cut_list):
        try:
            cut_list[i] = cn_model.key_to_index[word]
        except KeyError:
            cut_list[i] = 0
        pass
    # padding
    tokens_pad = tf.keras.preprocessing.sequence.pad_sequences([cut_list],
                                                               maxlen=int(71),
                                                               padding='pre',
                                                               truncating='pre')
    # 大于50000的归0，不归0模型的使用会报错
    tokens_pad[tokens_pad >= 50000] = 0
    return tokens_pad
def get_list(date):
    res=int(time.mktime(time.strptime(date,"%a %b %d %H:%M:%S %Y")))
    return res
def check_time(date):
    flag=True
    try:
     res=int(time.mktime(time.strptime(date,"%a %b %d %H:%M:%S %Y")))
    except:
     flag =False
    finally:
     return flag
def sort_CSV(uid):
    f = open("D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv", 'r',encoding='utf-8', errors='ignore')
    csvreader = csv.reader(f)
    data_list = list(csvreader)
    data_clean=[]
    for i in len(data_list):
        item=data_list[i]
        date= item[0]
    if check_time(date) :
        data_clean.append(item)
    # print(data_list)
    data_list1 =sorted(data_clean,key=lambda data_clean:get_list(data_clean[0]) )
    # print(data_list1)
    return data_list1
def sortCSV(uid):
    f = open("D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv", 'r',encoding='utf-8', errors='ignore')
    csvreader = csv.reader(f)
    data_list = list(csvreader)
    data_list1 =sorted(data_list,key=lambda data_list:get_list(data_list[0]) )
    return data_list1
class Count:
    def __init__(self, emo, indexs,qindex,qnum,ave,num):
        self.emo = emo
        self.indexs = indexs
        self.qindex = qindex
        self.qnum = qnum
        self.ave = ave
        self.num = num
def convert2(time):
    list=time.split()
    res=''
    for i in [4,1,2]:
        if(i!=2):
            res+=list[i]+" "
        else:
            res+=list[i]
    return res
def analyse(uid,cn_model,model,size,userdata):
    indexs={}
    nums={}
    for i in range(len(userdata)):
        item=userdata[i]#取出csv文件的每一行
        tokens_pad=predict_sentiment_index(item[1],cn_model)
        result = model.predict(x=tokens_pad)#调用模型分析
        temp =indexs.get(convert2(item[0]))#字典中是否含有键为该行时间的项
        if(temp):
            indexs[convert2(item[0])]+=result[0][1]#相应字典时间项加上分析结果的pos值
            nums[convert2(item[0])]+=1#该天条数加1
        else:
            if(i!=0):
                indexs[convert2(item[0])]=result[0][1]#新建一个该时间的值的项
                nums[convert2(item[0])]=1#新建一个该数据的项
            else:
                indexs[convert2(item[0])]=result[0][1]
                nums[convert2(item[0])]=1
    final=[]#最后的数据
    qindex=queue.Queue(maxsize=size)#值的队列
    qnums =queue.Queue(maxsize=size)#次数的队列
    ave = 0#近五天积极指数的总
    num = 0#近五天条数的总
    for time in indexs:
        timedata={}#每一个时间的数据
        date = time
        timedata["time"]=date
        if(qindex.full()):
            ave-=qindex.get()
            num-=qnums.get()
            qindex.put(indexs[time])
            qnums.put(nums[time])
            ave+=indexs[time]
            num+=nums[time]
        else:
            qindex.put(indexs[time])
            qnums.put(nums[time])
            ave+=indexs[time]
            num+=nums[time]
        value = indexs[time]/nums[time]
        timedata["single_value"] =value
        value = ave/num
        timedata["total_value"] =value
        final.append(timedata)
    with open("D:/IDEA_workspace/NLPStudy01/.idea/json/"+str(uid)+"/"+"emotion_"+str(uid)+".json", "w") as f:
        f.write(json.dumps(final, ensure_ascii=False, indent=4, separators=(',', ':')))
def analysecatagory(uid,cn_model,model,size,userdata):
    p0=Count(0,{},queue.Queue(maxsize=size),queue.Queue(maxsize=size),0,0)
    p1=Count(1,{},queue.Queue(maxsize=size),queue.Queue(maxsize=size),0,0)
    p2=Count(2,{},queue.Queue(maxsize=size),queue.Queue(maxsize=size),0,0)
    p3=Count(3,{},queue.Queue(maxsize=size),queue.Queue(maxsize=size),0,0)
    p4=Count(4,{},queue.Queue(maxsize=size),queue.Queue(maxsize=size),0,0)
    p5=Count(5,{},queue.Queue(maxsize=size),queue.Queue(maxsize=size),0,0)
    list={p0,p1,p2,p3,p4,p5}
    emos= ["angry","fear","happy","neutral","sad","surprise"]
    nums={}
    for i in range(len(userdata)):
        item=userdata[i]
        tokens_pad = predict_sentiment_catagory(item[1],cn_model)
        result = model.predict(x=tokens_pad)
        temp =p0.indexs.get(convert2(item[0]))
        if(temp):
            for p in list:
                p.indexs[convert2(item[0])]+=result[0][p.emo]
            nums[convert2(item[0])]+=1
        else:
            if(i!=0):
                for p in list:
                    p.indexs[convert2(item[0])]=result[0][p.emo]
                nums[convert2(item[0])]=1
            else:
                for p in list:
                    p.indexs[convert2(item[0])]=result[0][p.emo]
                nums[convert2(item[0])]=1
    collect=[]
    for time in p0.indexs:
        date = time
        timedata={}
        timedata["time"]=date
        for p in list:
            if(p.qindex.full()):
                p.ave-=p.qindex.get()
                p.num-=p.qnum.get()
                p.qindex.put(p.indexs[time])
                p.qnum.put(nums[time])
                p.ave+=p.indexs[time]
                p.num+=nums[time]
            else:
                p.qindex.put(p.indexs[time])
                p.qnum.put(nums[time])
                p.ave+=p.indexs[time]
                p.num+=nums[time]
            value = p.indexs[time]/nums[time]
            timedata["single_"+str(emos[p.emo])+"_value"]=value
            value = p.ave/p.num
            timedata["total_"+str(emos[p.emo])+"_value"]=value
        collect.append(timedata)
    with open("D:/IDEA_workspace/NLPStudy01/.idea/json/"+str(uid)+"/"+"catagory_"+str(uid)+".json", "w") as f:
        f.write(json.dumps(collect, ensure_ascii=False, indent=4, separators=(',', ':')))
def init():
    global cn_model
    global catagory_model
    global index_model
    global tokens_length
    cn_model = KeyedVectors.load_word2vec_format('D:/IDEA_workspace/NLPStudy01/.idea/source/sgns.zhihu.bigram-char',
                                                 binary=False, unicode_errors='ignore')
    catagory_model = tf.keras.models.load_model("D:/IDEA_workspace/NLPStudy01/.idea/model/catagory_model.h5")
    index_model=tf.keras.models.load_model("D:/IDEA_workspace/NLPStudy01/.idea/model/nlp_model7.h5")
    y = []
    with open("D:/IDEA_workspace/NLPStudy01/.idea/data/usual_all.txt",'r',encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        y.append(item['label'])
    encoder = preprocessing.LabelEncoder()
    y_tokens = encoder.fit_transform(y)
    y_tokens = tf.keras.utils.to_categorical(y_tokens)
    print(y_tokens)
    tokens_length = 75
    print("初始化完成")

if __name__ == '__main__':
    uid =7089246227
    init()
    time_start=time.time()
    mkdir(savePath+str(uid)+"/")
    spider(uid)
    userdata=sortCSV(uid)
    analyse(uid,cn_model,index_model,5,userdata )
    analysecatagory(uid,cn_model,catagory_model,5,userdata)
    time_end=time.time()
    print('totally cost',time_end-time_start)
