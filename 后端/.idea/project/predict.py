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
import function

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
def analyse(uid,cn_model,catagory_model,index_model,size,userdata):
    indexs={}
    nums={}
    for i in range(len(userdata)):
        item=userdata[i]
        tokens_pad=predict_sentiment_index(item[1],cn_model)
        result = index_model.predict(x=tokens_pad)
        temp =indexs.get(convert2(item[0]))
        if(temp):
            indexs[convert2(item[0])]+=result[0][1]
            nums[convert2(item[0])]+=1
        else:
            if(i!=0):
                indexs[convert2(item[0])]=result[0][1]
                nums[convert2(item[0])]=1
            else:
                indexs[convert2(item[0])]=result[0][1]
                nums[convert2(item[0])]=1
    final=[]
    qindex=queue.Queue(maxsize=size)
    qnums =queue.Queue(maxsize=size)
    ave = 0
    num = 0
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
        result = catagory_model.predict(x=tokens_pad)
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
        timedata={}
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
    with open("D:/IDEA_workspace/NLPStudy01/.idea/json/"+str(uid)+"/"+"data_"+str(uid)+".json", "w") as f:
        f.write(json.dumps(collect, ensure_ascii=False, indent=4, separators=(',', ':')))
def contain_word(sentences,word):     #定义函数实现分词
    cutsentence = jieba.lcut(sentences.strip())     #精确模式
    stopwords = word      # 这里加载停用词的路径
    flag=False
    for word in cutsentence:     #for循环遍历分词后的每个词语
        if word==stopwords:     #判断分词后的词语是否在停用词表内
            flag =True
            break
    return flag
def analyse_word(uid,cn_model,catagory_model,index_model,size,old_userdata,word):
    userdata=[]
    print(len(old_userdata))
    for i in range(len(old_userdata)):
        item=old_userdata[i]
        if(contain_word(item[1],word)):
            userdata.append(item)
    indexs={}
    nums={}
    for i in range(len(userdata)):
        item=userdata[i]
        tokens_pad=predict_sentiment_index(item[1],cn_model)
        result = index_model.predict(x=tokens_pad)
        temp =indexs.get(convert2(item[0]))
        if(temp):
            indexs[convert2(item[0])]+=result[0][1]
            nums[convert2(item[0])]+=1
        else:
            if(i!=0):
                indexs[convert2(item[0])]=result[0][1]
                nums[convert2(item[0])]=1
            else:
                indexs[convert2(item[0])]=result[0][1]
                nums[convert2(item[0])]=1
    final=[]
    qindex=queue.Queue(maxsize=size)
    qnums =queue.Queue(maxsize=size)
    ave = 0
    num = 0
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
        result = catagory_model.predict(x=tokens_pad)
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
        timedata={}
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
    with open("D:/IDEA_workspace/NLPStudy01/.idea/json/"+str(uid)+"/"+"data_"+word+"_"+str(uid)+".json", "w") as f:
        f.write(json.dumps(collect, ensure_ascii=False, indent=4, separators=(',', ':')))
if __name__ == "__main__":
    print("初始化模块")
    cn_model = KeyedVectors.load_word2vec_format('D:/IDEA_workspace/NLPStudy01/.idea/source/sgns.zhihu.bigram-char',
                                             binary=False, unicode_errors='ignore')
    catagory_model = tf.keras.models.load_model("D:/IDEA_workspace/NLPStudy01/.idea/model/catagory_model.h5")
    index_model=tf.keras.models.load_model("D:/IDEA_workspace/NLPStudy01/.idea/model/nlp_model7.h5")
    print("初始化完成")
    uid=7089246227
    old_userdata=function.sortCSV(uid)
    analyse_word(uid,cn_model,catagory_model,index_model,5,old_userdata, "力量" )