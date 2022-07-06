import socket
import sys
import threading
import json
import numpy as np
import function
import spider
import tensorflow as tf
import os
import predict
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from gensim.models import KeyedVectors
import wordscloud
print("初始化模型")
cn_model = KeyedVectors.load_word2vec_format('D:/IDEA_workspace/NLPStudy01/.idea/source/sgns.zhihu.bigram-char',
                                             binary=False, unicode_errors='ignore')
catagory_model = tf.keras.models.load_model("D:/IDEA_workspace/NLPStudy01/.idea/model/catagory_model.h5")
index_model=tf.keras.models.load_model("D:/IDEA_workspace/NLPStudy01/.idea/model/nlp_model7.h5")
tokens_length = 75
print("初始化完成")
class ServerThreading(threading.Thread):
    def __init__(self,clientsocket,recvsize=1024*1024,encoding="utf-8"):
        threading.Thread.__init__(self)
        self._socket = clientsocket
        self._recvsize = recvsize
        self._encoding = encoding
        pass

    def run(self):
        print("开启线程.....")
        try:
            msg = ''
            while True:
                # 读取recvsize个字节
                rec = self._socket.recv(self._recvsize)
                # 解码
                msg += rec.decode(self._encoding)
                # 文本接受是否完毕，因为python socket不能自己判断接收数据是否完毕，
                # 所以需要自定义协议标志数据接受完毕
                if msg.strip().endswith('over'):
                    msg=msg[:-4]
                    break
            print("信息接收完成")
            if(msg.strip().startswith('ana')):
                print("开始分析用户情绪")
                msg=msg[3:]
                uid = int(msg)
                savePath ="D:/IDEA_workspace/NLPStudy01/.idea/json/"
                if(os.path.exists(savePath+str(uid)+'/data_'+str(uid)+'.json')):
                    sendmsg=open('D:/IDEA_workspace/NLPStudy01/.idea/json/'+str(uid)+'/data_'+str(uid)+'.json', 'r',encoding= 'utf-8').read()
                    self._socket.send(("%s"%sendmsg).encode(self._encoding))
                else:
                # 调用神经网络模型处理请求
                    function.mkdir(savePath+str(uid)+"/")
                    spider.spider(uid)
                    userdata=function.sortCSV(uid)
                    print("数据处理好")
                # function.analyse(uid,cn_model,index_model,5,userdata)
                    predict.analyse(uid,cn_model,catagory_model,index_model,5,userdata)
                # 发送数据
                    sendmsg=open('D:/IDEA_workspace/NLPStudy01/.idea/json/'+str(uid)+'/data_'+str(uid)+'.json', 'r',encoding= 'utf-8').read()
                    self._socket.send(("%s"%sendmsg).encode(self._encoding))
                        #os.remove("D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv")
            elif(msg.strip().startswith('wor')):
                print("开始创造词云")
                msg=msg[3:]
                uid = int(msg)
                savePath ="D:/IDEA_workspace/NLPStudy01/.idea/json/"
                if(os.path.exists("D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv")):
                    if(not os.path.exists(savePath+str(uid)+'/wordcloud_'+str(uid)+'.png')):
                        wordscloud.main(uid)
                        print("词云完成")
                    # sendmsg=open(savePath+str(uid)+'/wordcloud_'+str(uid)+'.png', 'r',encoding= 'utf-8').read()
                    # self._socket.send(("%s"%sendmsg).encode(self._encoding))
                    filepath=savePath+str(uid)+'/wordcloud_'+str(uid)+'.png'
                    fp = open(filepath, 'rb')
                    while True:
                        data = fp.read(1024)  # 读入图片数据
                        if not data:
                            print('{0} send over...'.format(filepath))
                            break
                        self._socket.send(data)  # 以二进制格式发送图片数据
                else:
                    self._socket.send("请先点击用户趋势".encode(self._encoding))
            elif(msg.strip().startswith('edi')):
                print("开始分析合订本趋势")
                uid = int(msg[3:13])
                word= msg[13:]
                savePath ="D:/IDEA_workspace/NLPStudy01/.idea/json/"
                if(os.path.exists(savePath+str(uid)+'/data_'+word+"_"+str(uid)+'.json')):
                    sendmsg=open('D:/IDEA_workspace/NLPStudy01/.idea/json/'+str(uid)+'/data_'+word+"_"+str(uid)+'.json', 'r',encoding= 'utf-8').read()
                    self._socket.send(("%s"%sendmsg).encode(self._encoding))
                else:
                    # 调用神经网络模型处理请求
                    # function.mkdir(savePath+str(uid)+"/")
                    # spider.spider(uid)
                    userdata=function.sortCSV(uid)
                    # function.analyse(uid,cn_model,index_model,5,userdata)
                    predict.analyse_word(uid,cn_model,catagory_model,index_model,5,userdata,word)
                    # 发送数据
                    sendmsg=open('D:/IDEA_workspace/NLPStudy01/.idea/json/'+str(uid)+'/data_'+word+"_"+str(uid)+'.json', 'r',encoding= 'utf-8').read()
                    self._socket.send(("%s"%sendmsg).encode(self._encoding))
        except Exception as identifier:
            self._socket.send("500".encode(self._encoding))
            print(identifier)
            pass
        finally:
            self._socket.close()
        print("任务结束.....")

        pass

    def __del__(self):

        pass
if __name__ == "__main__":
    # 创建服务器套接字
    serversocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 获取本地主机名称
    # host = socket.gethostname()
    host =''
    # 设置一个端口
    port = 10086
    # 将套接字与本地主机和端口绑定
    serversocket.bind((host,port))
    # 设置监听最大连接数
    serversocket.listen(5)
    # 获取本地服务器的连接信息
    myaddr = serversocket.getsockname()
    print("服务器地址:%s"%str(myaddr))
    # 循环等待接受客户端信息
    while True:
        # 获取一个客户端连接
        clientsocket,addr = serversocket.accept()
        print("连接地址:%s" % str(addr))
        try:
            t = ServerThreading(clientsocket)#为每一个请求开启一个处理线程
            t.start()
            pass
        except Exception as identifier:
            print(identifier)
            pass
        pass
    serversocket.close()
    pass