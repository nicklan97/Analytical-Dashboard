import pandas as pd
import re
import jieba
from pymongo import MongoClient
from jieba import analyse
from collections import Counter
from itertools import chain
import json
from functools import lru_cache


@lru_cache(maxsize=128)
def get_df():

    client = MongoClient('localhost', 27017)
    db = client['lagou']
    df = pd.DataFrame(list(db['PositionDetail'].find({}, {'_id': 0, 'positionName': 1,
                                                          'positionDetail': 1})))

    df['positionDetail'] = df['positionDetail'].apply(lambda x: re.compile(
        r'<[^>]+>', re.S).sub('', x).replace('\n', '').replace('&NBSP;', '').replace('\r', ' '))
    df['positionDetail'] = df['positionDetail'].apply(lambda x: x.replace('岗位职责', '职位职责').replace('工作职责', '职位职责').replace(
        '工作内容', '职位职责').replace('岗位描述', '职位职责').replace('【在这里，你将......】', '职位职责').replace('工作描述', '职位职责'))
    df['positionDetail'] = df['positionDetail'].apply(lambda x: x.replace('【我们期待这样的你】', '职位要求').replace(
        '任职资格', '职位要求').replace('任职要求', '职位要求').replace('工作要求', '职位要求').replace('岗位要求', '职位要求'))
    df = df[df['positionDetail'].str.contains('职位要求')].reset_index(drop=True)
    df['positionName'] = df['positionName'].apply(lambda x: re.sub(u"\\（.*?\\）|\\{.*?}|\\[.*?]", "", x).upper()
                                                  .replace('（', '').replace('）', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
                                                  )
    df['positionDetail'] = df['positionDetail'].apply(lambda x: x.upper())
    punc = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}'
    df['positionreq'] = df['positionDetail'].apply(lambda x: re.sub(
        r"[%s]+" % punc, "", x)).apply(lambda x: x.split('职位要求')[1].replace(' ', ''))
    skilldata = read_file('skilldata.txt')
    for i in skilldata:
        jieba.add_word(i)
    tfidf = analyse.extract_tags
    df['tags'] = df['positionreq'].apply(lambda x: tfidf(x))
    print('finish loading')
    return df


def read_file(file_name):
    fp = open(file_name, "r", encoding="utf-8")
    content_lines = fp.readlines()
    fp.close()
    for i in range(len(content_lines)):
        content_lines[i] = content_lines[i].rstrip("\n")
    print('finsih reading')
    return content_lines


def searchskill(job, data):
    if job.islower() == True:
        job = job.upper()
    fil = read_file('filter.txt')
    if '++' in job:
        job = job.replace('++', '\++')
    din = data[data['positionName'].str.contains(job)]
    df = pd.Series(Counter(chain(*din.tags))
                   ).sort_index().rename_axis('skills').reset_index(name='count')
    for tag in list(df['skills']):
        if tag in fil:
            df.drop(df[df['skills'] == tag].index, inplace=True)
    df = df.sort_values(by='count', ascending=False).head(30).reset_index(drop=True)
    output = json.loads(df.to_json(orient='records'))
    print('finish search')
    return output, job
