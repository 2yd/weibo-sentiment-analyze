import sys
import time
import re
import jieba
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator#, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image
import re
import jieba
import csv
from cnsenti import Sentiment
from time import sleep

stopWordsPath = "D:/IDEA_workspace/NLPStudy01/.idea/source/stopword01.txt"
def plt_imshow(x, ax=None, show=True):
    if ax is None:
        fig, ax = plt.subplots()
    ax.imshow(x)
    ax.axis("off")
    if show: plt.show()
    return ax

def count_frequencies(word_list):
    freq = dict()
    for w in word_list:
        if w not in freq.keys():
            freq[w] = 1
        else:
            freq[w] += 1
    return freq

def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords

def cutsentences(sentences, filepath):     #定义函数实现分词
    print('原句子为：'+ sentences)
    cutsentence = jieba.lcut(sentences.strip())     #精确模式
    print ('\n'+'分词后：'+ "/ ".join(cutsentence))
    stopwords = stopwordslist(filepath)     # 这里加载停用词的路径
    lastsentences = ''
    for word in cutsentence:     #for循环遍历分词后的每个词语
        if word not in stopwords:     #判断分词后的词语是否在停用词表内
            if word != '\t':
                lastsentences += word
    print('\n'+'去除停用词后：'+ lastsentences)
    return lastsentences

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
def main(uid):
    file="D:/IDEA_workspace/NLPStudy01/.idea/data/"+str(uid)+".csv"
    fname_stop = stopWordsPath
    fname_mask = "D:/IDEA_workspace/NLPStudy01/.idea/source/img.png"
    fname_font = "D:/IDEA_workspace/NLPStudy01/.idea/source/SourceHanSerifK-Light.otf"

    # read in texts (an article)
    f = open(file , 'r',encoding='utf-8')
    csvreader = csv.reader(f)
    data_list = list(csvreader)
    text=''
    for i in range(len(data_list)):
       item=data_list[i]
       text+=item[1]
    # text =clean(text)
    # Chinese stop words
    STOPWORDS_CH = open(fname_stop, encoding='utf8').read().split()

    # processing texts: cutting words, removing stop-words and single-charactors
    word_list = [
        w for w in jieba.cut(text)
        if w not in set(STOPWORDS_CH) and len(w) > 1
    ]
    freq = count_frequencies(word_list)
    # processing image
    im_mask = np.array(Image.open(fname_mask))
    im_colors = ImageColorGenerator(im_mask)

    # generate word cloud
    wcd = WordCloud(font_path=fname_font, # font for Chinese charactors
                background_color='white',
                mode="RGBA",
                mask=im_mask,
                )
    #wcd.generate(text) # for English words
    wcd.generate_from_frequencies(freq)
    wcd.recolor(color_func = im_colors)

    # visualization
    ax = plt_imshow(wcd,)
    ax.figure.savefig(f'D:/IDEA_workspace/NLPStudy01/.idea/json/'+str(uid)+'/wordcloud_'+str(uid)+'.png', bbox_inches='tight', dpi=150)
if __name__ == '__main__':
    # setting paths
    uid=7089246227
    main(uid)