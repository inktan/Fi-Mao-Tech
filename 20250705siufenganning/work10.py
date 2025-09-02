import re
import os
import pandas as pd
import numpy as np
import jieba
import jieba.analyse
import collections
import glob
import pysenti
import matplotlib.pyplot as plt
from pandas import Series, DataFrame

%matplotlib inline 
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

file = open(up +"hit_stopwords.txt",encoding='utf8') 
stopword = [line.lstrip().rstrip() for line in file.readlines()]
file.close()

#清洗数据，带有词性的分词，清洗数据
def removeStopword(sentence):
    sentence = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[\]\[：:；+——！，。？、~@#￥%……&*（）]+|[\d+]|[a-zA-Z+]|⊙|∀|·|【|】", "",str(sentence))
    sentence = sentence.replace('-','')
    sentence_seged = jieba.posseg.cut(sentence.strip())
    outstr = ''
    word_list = []
    for x in sentence_seged:
        if ('\u4e00' <= x.word <= '\u9fa5' and x.word not in stopword):
            outstr ="{}/{}".format(x.word,x.flag)
            word_list.append(outstr)
    return ' '.join(word_list)

#清洗数据，没有词性的分词，清洗数据
def removeStopword_text(sentence):
    sentence = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[\]\[：:；+——！，。？、~@#￥%……&*（）]+|[\d+]|[a-zA-Z+]|⊙|∀|·|【|】", "",str(sentence))
    sentence = sentence.replace('-','')
    sentence_seged = jieba.posseg.cut(sentence.strip())
    outstr = ''
    word_list = []
    for x in sentence_seged:
        if ('\u4e00' <= x.word <= '\u9fa5' and x.word not in stopword):
            outstr ="{}".format(x.word)
            word_list.append(outstr)
    return ' '.join(word_list)

def getS(x):
    if x>0.1:
        return "积极"
    if x < -0.1:
        return "消极"
    return "中性"
import json
import pandas as pd
import re
def parse_jsonp(jsonp_str):
    match = re.match(r'^\w+\((.*)\)$', jsonp_str.strip())
    if not match:
        raise ValueError("Invalid JSONP format")
    json_str = match.group(1)
    return json.loads(json_str)

import jieba
import collections
def getWordCount(jb,wo):
    word_counts = collections.Counter(jb)
    num = 0
    for w in wo:
        num+=word_counts[w]
    return num
def getlist(x):
    return list(jieba.cut(x))
for w in  df1.columns:
    df[w] =  df['text_list'].apply(lambda x : getWordCount(x,df1[w].dropna().tolist()))
    #加载包
import numpy as np
import os
import pickle
import io
import re
import jieba
import random
import collections
import pandas as pd
import glob
import collections
import jieba.analyse
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image,ImageSequence
from snownlp import SnowNLP
%matplotlib inline
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False  

def get_word_list(p):
    file = open(p,encoding='utf8') 
    words = [line.lstrip().rstrip() for line in file.readlines()]
    file.close()
    return words
#数据处理
def seg_word(text):
    text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+|[\d+]|[a-zA-Z+]|⊙|∀|·|【|】", "",str(text))
    text = text.replace('-','')
    word_list = [i for i in jieba.cut(text) if i not in stopword]
    return word_list

def removeStopword(sentence):
    sentence = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[\]\[：:；+——！，。？、~@#￥%……&*（）]+|[\d+]|[a-zA-Z+]|⊙|∀|·|【|】", "",str(sentence))
    sentence = sentence.replace('-','')
    sentence_seged = jieba.posseg.cut(sentence.strip())
    outstr = ''
    word_list = []
    for x in sentence_seged:
        if ('\u4e00' <= x.word <= '\u9fa5' and x.word not in stopword):
            outstr ="{}/{}".format(x.word,x.flag)
            word_list.append(outstr)
    return ' '.join(word_list)

def removeStopword_keyword_txt(sentence):
    '''
    带词性标注，对句子进行分词，不排除停词等
    :param sentence:输入字符
    :return:
    '''
    sentence = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[\]\[：:；+——！，。？、~@#￥%……&*（）]+|[\d+]|[a-zA-Z+]|⊙|∀|·|【|】", "",str(sentence))
    sentence = sentence.replace('-','')
    sentence_seged = jieba.posseg.cut(sentence.strip())
    outstr = ''
    word_list = []
    for x in sentence_seged:
        if ('\u4e00' <= x.word <= '\u9fa5' and x.word not in stopword):
            outstr ="{}".format(x.word)
            word_list.append(outstr)
    return ' '.join(word_list)

def keyword_exact(text):
    text = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+|[\d+]|[a-zA-Z+]|⊙|∀|·|【|】", "",str(text))
    text = text.replace('-','')
    text = ''.join([i for i in jieba.cut(text) if i not in stopword])
    tags = jieba.analyse.extract_tags(text, topK=200)
    return" ".join(tags)

def classify_words(dict_data):
    z = 0
    data = []
    for k,v in enumerate(dict_data):     
        w = 0
        if v in positive_words:   #为正面情感词
            w += 1        
            #print(v)
            for i in range(z, int(k)):
                if dict_data[i] in privative_words:
                    for j in range(z, i):   #程度词+否定词+情感词
                        if (dict_data[j] in adverb_of_degree_words6 or dict_data[j] in adverb_of_degree_words5 or \
                                dict_data[j] in adverb_of_degree_words4 or dict_data[j] in adverb_of_degree_words3 or \
                                dict_data[j] in adverb_of_degree_words2 or dict_data[j] in adverb_of_degree_words1):
                            w = w * (-1) * 2
                            #print(w)
                        break
                    for j in range(i, int(k)):  #否定词+程度词+情感词
                        if (dict_data[j] in adverb_of_degree_words6 or dict_data[j] in adverb_of_degree_words5 or \
                                dict_data[j] in adverb_of_degree_words4 or dict_data[j] in adverb_of_degree_words3 or \
                                dict_data[j] in adverb_of_degree_words2 or dict_data[j] in adverb_of_degree_words1):
                            w = w * 0.5
                            #print(w)
                        break
                elif dict_data[i] in adverb_of_degree_words1:
                    w =w * 2
                    #print(w)
                elif dict_data[i] in adverb_of_degree_words2:
                    w =w * 1.5
                    #print(w)
                elif dict_data[i] in adverb_of_degree_words3:
                    w =w * 1.25
                    #print(w)
                elif dict_data[i] in adverb_of_degree_words4:
                    w =w * 1.2
                    #print(w)
                elif dict_data[i] in adverb_of_degree_words5:
                    w =w * 0.8
                    #print(w)
                elif dict_data[i] in adverb_of_degree_words6:
                    w =w * 0.5
                    #print(w)
            z = int(k) + 1
        if v in negative_words:   #为负面情感词
            w -= 1
            for i in range(z, int(k)):
                if dict_data[i] in privative_words:
                    for j in range(z, i):
                        #程度词+否定词+情感词
                        if (dict_data[j] in adverb_of_degree_words6 or dict_data[j] in adverb_of_degree_words5 or \
                                dict_data[j] in adverb_of_degree_words4 or dict_data[j] in adverb_of_degree_words3 or \
                                dict_data[j] in adverb_of_degree_words2 or dict_data[j] in adverb_of_degree_words1):
                            w = w * (-1)*2
                        break
                    for j in range(i,int(k)):
                        #否定词+程度词+情感词
                        if (dict_data[j] in adverb_of_degree_words6 or dict_data[j] in adverb_of_degree_words5 or \
                                 dict_data[j] in adverb_of_degree_words4 or dict_data[j] in adverb_of_degree_words3 or \
                                 dict_data[j] in adverb_of_degree_words2 or dict_data[j] in adverb_of_degree_words1):
                                w = w * 0.5
                        break
                if dict_data[i] in adverb_of_degree_words1:
                    w *= 2
                elif dict_data[i] in adverb_of_degree_words2:
                    w *= 1.5
                elif dict_data[i] in adverb_of_degree_words3:
                    w *= 1.25
                elif dict_data[i] in adverb_of_degree_words4:
                    w *= 1.2
                elif dict_data[i] in adverb_of_degree_words5:
                    w *= 0.8
                elif dict_data[i] in adverb_of_degree_words6:
                    w *= 0.5
            z = int(k)+1
        data.append(w)
    seg = np.sum(data)
    return seg

#调用用情感分析
def appaly_seg(text):
    #切词
    word_list = seg_word(text)
    #情感分析
    seg = classify_words(word_list)
    return seg

up = r"K:\python_project\software\有用代码\软件系列/"
flags = ('n', 'an','nr', 'ns', 'nt', 'nz', 'v','vn','vd','d','vg','vl','nl','ng','a','al','z','b')
stopword = get_word_list(up + "词典情感分析/停用词.txt")
positive_words = get_word_list(up + "词典情感分析/正面情绪词.txt")
negative_words = get_word_list(up + "词典情感分析/负面情绪词.txt")
privative_words = get_word_list(up + "词典情感分析/否定词.txt")
adverb_of_degree_words1 = get_word_list(up + "词典情感分析/2倍.txt")
adverb_of_degree_words2 = get_word_list(up + "词典情感分析/1.5倍.txt")
adverb_of_degree_words3 = get_word_list(up + "词典情感分析/1.25倍.txt")
adverb_of_degree_words4 = get_word_list(up + "词典情感分析/1.2倍.txt")
adverb_of_degree_words5 = get_word_list(up + "词典情感分析/0.8倍.txt")
adverb_of_degree_words6 = get_word_list(up + "词典情感分析/0.5倍.txt")
jieba.load_userdict(up + '词典情感分析/正面情绪词.txt')
jieba.load_userdict(up + '词典情感分析/负面情绪词.txt')

df['情感值'] = df['评论或介绍'].apply(lambda x:appaly_seg(x))

def hasin(text,words):
    for w in words:
        if w in text:
            return 1
    return 0 
def gettexindexlistindex(text,words):
    lines = re.split("。|？|！",str(text))
    all_text = []
    for line in lines:
        if hasin(line,words):
            all_text.append(line)
    if len(all_text):
        texttes = " ".join(all_text)
        return appaly_seg(texttes)
    return 0

dir(df1)
for w in  df1.columns:
    df[w + "情感"] =  df['评论或介绍'].apply(lambda x : gettexindexlistindex(x,df1[w].dropna().tolist()))

clist = []
for c in df1.columns:
    c1 = df[df[c] !=0].shape[0]
    clist.append(c1)

plt.figure(figsize=(6,6))
plt.pie(clist,labels= df1.columns ,autopct='%1.1f%%')
plt.axis("equal")
plt.title('情感分析饼状图')
plt.xlabel('饼状图')
plt.show()

import seaborn as sns
sns.kdeplot(df['娱乐情感'], shade=True, color="g", label="Cyl=4", alpha=1)

df.to_excel(up1+"情感.xlsx")