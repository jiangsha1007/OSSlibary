
from ast import literal_eval
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import sparse as sp_sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
import nltk
import codecs
import re
from nltk.corpus import stopwords
from model.common_model import *
import re
from bs4 import BeautifulSoup

#nltk.download('stopwords')
#stop_words = set(stopwords.words('english'))

def write_tsv():
    f = codecs.open('train.tsv', 'a+')
    f2 = codecs.open('test.tsv', 'a+')
    f3 = codecs.open('pre.tsv', 'a+')
    f.write('describe\ttags\n')
    f2.write('describe\ttags\n')
    f3.write('id\tdescribe\n')
    oss_all = OsslibMetadata.select()
    index = 0
    for per_oss_info in oss_all:
        topic_info = OsslibTopic.select(OsslibTopic.q.oss_id == per_oss_info.community_id)
        oss_readme = per_oss_info.readme
        oss_descripe = per_oss_info.oss_description
        if (oss_readme == None or oss_readme == '') and (oss_descripe == None or oss_descripe == ''):
            continue
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        try:
            match = zhPattern.search(oss_readme)
        except:
            match = zhPattern.search(oss_descripe)

        if match:
            continue
        if oss_readme != None:
            soup = BeautifulSoup(oss_readme, 'html.parser')
            oss_readme = soup.get_text().replace('=', '').replace('#', '').replace('\r', '').replace('\n', '').replace(
                '\t', '')
        else:
            oss_readme = ''
        if oss_descripe != None:
            oss_descripe = oss_descripe.replace('\r', '').replace('\n', '').replace('\t', '')
        else:
            oss_descripe = ''

        topic_item = []
        print(per_oss_info.community_id)
        if topic_info.count() > 0:
            if index < 7500:
                for per_topic_info in topic_info:
                    topic_item.append(per_topic_info.topic)
                try:
                    topic_item = topic_item[0:3]
                    f.write(oss_descripe + " " + oss_readme + '\t' + str(topic_item) + '\n')
                except:
                    continue
            else:
                for per_topic_info in topic_info:
                    topic_item.append(per_topic_info.topic)
                try:
                    topic_item = topic_item[0:3]
                    f2.write(oss_descripe + " " + oss_readme + '\t' + str(topic_item) + '\n')
                except:
                    continue
            index += 1
        else:
            try:
                f3.write(str(per_oss_info.community_id) + '\t' + oss_descripe + " " + oss_readme + '\n')
            except BaseException as ex:
                print(ex)
                continue


    f.close()
    f2.close()
    f3.close()

def read_data(filename):
    data = pd.read_csv(filename, sep='\t', encoding='ANSI')
    data['tags'] = data['tags'].apply(literal_eval)
    return data

def show():
    train = read_data('train.tsv')
    tags = train['tags'].values
    tag_dic = {}
    for tag_list in tags:
        for tag in tag_list:
            if tag not in tag_dic:
                tag_dic[tag] = 1
            else:
                tag_dic[tag] += 1
    df = pd.DataFrame(list(tag_dic.items()), columns=['tag', 'count']).sort_values(by='count', axis=0, ascending=False)
    print('标签总数:', len(df))
    print(df.head(10))

    df[:10].plot(x='tag', y='count', kind='bar', legend=False, grid=True, figsize=(10, 6), fontsize=18)
    plt.title("每个标签的分布", fontsize=18)
    plt.ylabel('出现次数', fontsize=18)
    plt.xlabel('标签', fontsize=18)
    plt.show()
    '''
    tagCount = train['tags'].apply(lambda x: len(x))
    x = tagCount.value_counts()
    # plot
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x.index, x.values)
    plt.title("标签数量分布", fontsize=15)
    plt.ylabel('repo num', fontsize=15)
    plt.xlabel('label num', fontsize=15)
    plt.show()
'''

def train():
    train = read_data('train.tsv')
    test = read_data('test.tsv')
    #pre = read_data('pre.tsv')
    X_train, y_train = train['describe'], train['tags']
    X_test, y_test = test['describe'], test['tags']
    # 开始进行数据清洗
    X_train = [text_prepare(x) for x in X_train]
    X_test = [text_prepare(x) for x in X_test]
    # 生成多标签的词袋矩阵
    tag_dic = {}
    tags = y_train.values
    for tag_list in tags:
        for tag in tag_list:
            if tag not in tag_dic:
                tag_dic[tag] = 1
            else:
                tag_dic[tag] += 1
    tags = y_test.values
    for tag_list in tags:
        for tag in tag_list:
            if tag not in tag_dic:
                tag_dic[tag] = 1
            else:
                tag_dic[tag] += 1
    mlb = MultiLabelBinarizer(classes=sorted(tag_dic.keys()))
    y_train = mlb.fit_transform(y_train)
    y_test = mlb.fit_transform(y_test)
    print(y_train)
    SVC_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(min_df=5, max_df=0.9, ngram_range=(1, 2), token_pattern='(\S+)')),
        ('clf', OneVsRestClassifier(LinearSVC(), n_jobs=1)),
    ])
    SVC_pipeline.fit(X_train, y_train)
    predicted = SVC_pipeline.predict(X_train)
    print_evaluation_scores(y_train, predicted)


from sklearn.metrics import accuracy_score

from sklearn.metrics import f1_score

from sklearn.metrics import roc_auc_score

from sklearn.metrics import average_precision_score

from sklearn.metrics import recall_score


def print_evaluation_scores(y_val, predicted):
    accuracy = accuracy_score(y_val, predicted)
    f1_score_macro = f1_score(y_val, predicted, average='macro')
    f1_score_micro = f1_score(y_val, predicted, average='micro')
    f1_score_weighted = f1_score(y_val, predicted, average='weighted')
    print("accuracy:", accuracy)
    print("f1_score_macro:", f1_score_macro)
    print("f1_score_micro:", f1_score_micro)
    print("f1_score_weighted:", f1_score_weighted)


#用空格替换各种符号
REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
#删除各种符号
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
STOPWORDS = set(stopwords.words('english'))
#定义数据清洗函数
def text_prepare(text):
    text = text.lower() # 字母小写化
    text = REPLACE_BY_SPACE_RE.sub(' ',text)
    text = BAD_SYMBOLS_RE.sub('',text)
    text = ' '.join([w for w in text.split() if w not in STOPWORDS]) # 删除停用词
    return text


