from pymongo import MongoClient
import pandas as pd
import re
from functools import lru_cache
import json


@lru_cache(maxsize=128)
def get_df():
    client = MongoClient('localhost', 27017)
    db = client['lagou']
    df = pd.DataFrame(list(db['PositionDetail'].find({}, {'_id': 0, 'positionName': 1, 'salary': 1, 'workAddress': 1,
                                                          'industryField': 1, 'positionDetail': 1})))
    df['positionName'] = df['positionName'].apply(lambda x: re.sub(u"\\（.*?\\）|\\{.*?}|\\[.*?]", "", x).upper()
                                                  .replace('（', '').replace('）', '').replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
                                                  )
    df['positionDetail'] = df['positionDetail'].apply(lambda x: x.upper())
    df[['low-salary', 'high-salary']] = df.salary.str.split('-', expand=True)
    df['low-salary'] = df['low-salary'].apply(lambda x: int(
        x.replace('以上', '').replace('k', '000').replace('K', '000')))
    df.drop(['salary', 'high-salary'], axis=1, inplace=True)
    return df


def search_job_from_skill(skill, df):
    if skill.islower() == True:
        skill = skill.upper()
    data = df[df['positionDetail'].str.contains(skill)]
    total = len(data)
    ratio = round((total/len(df)), 4)*100
    output = pd.DataFrame(data['positionName'].value_counts()).rename(
        columns={'positionName': 'counts'}).head(30)
    salary = []
    bj = []
    sh = []
    gz = []
    sz = []
    hz = []
    cd = []
    wh = []
    for i in output.index:
        if '++' in i:
            i = i.replace('++', '\++')
        d = data[data['positionName'].str.contains('^'+i+'$')]
        i = i.replace('\++', '++')
        salary.append(round(d['low-salary'].median()))
        bj.append(len(data[(data['workAddress'] == '北京') & (data['positionName'] == i)]))
        sh.append(len(data[(data['workAddress'] == '上海') & (data['positionName'] == i)]))
        gz.append(len(data[(data['workAddress'] == '广州') & (data['positionName'] == i)]))
        sz.append(len(data[(data['workAddress'] == '深圳') & (data['positionName'] == i)]))
        hz.append(len(data[(data['workAddress'] == '杭州') & (data['positionName'] == i)]))
        cd.append(len(data[(data['workAddress'] == '成都') & (data['positionName'] == i)]))
        wh.append(len(data[(data['workAddress'] == '武汉') & (data['positionName'] == i)]))
    output['salary'] = salary
    output['bj'] = bj
    output['sh'] = sh
    output['gz'] = gz
    output['sz'] = sz
    output['hz'] = hz
    output['cd'] = cd
    output['wh'] = wh
    output['name'] = output.index
    output = json.loads(output.to_json(orient='records'))
    #output['Total'] = len(data)
    return output, total, skill, ratio


def get_industry(skill, df):
    if skill.islower() == True:
        skill = skill.upper()
    data = df[df['positionDetail'].str.contains(skill)]
    data['industryField'] = data['industryField'].apply(
        lambda x: x.replace('、', ',').replace(' ', ','))
    data['industryField'] = data['industryField'].str.split(',').explode().reset_index(drop=True)
    data = data[data['industryField'].notna()]
    output = pd.DataFrame(data['industryField'].value_counts()).rename(
        columns={'industryField': 'counts'}).head(30)
    output['industry'] = output.index
    return output
