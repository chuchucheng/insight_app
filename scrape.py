#!/usr/bin/env python
# coding: utf-8

# In[275]:


import requests

import pickle
import sys
import xgboost as xgb
from bs4 import BeautifulSoup
import datetime
import re
import numpy as np
import pandas as pd

from pandas.tseries.holiday import USFederalHolidayCalendar

def disnum(dislist):
    r= []
    for dis in dislist:
        dis = re.sub(r'%\s\w{3}','', dis)
        dis = int(dis)/100
        r.append(dis)
    if len(r) == 1:
        return r[0]
    elif len(r) == 0:
        return 0
    else:
        r = [1-x for x in r]
        return 1- np.prod(r)
    
def pastdays(pt):
    d = re.findall(r'\w*\sday',pt)
    if len(d) == 0:
        return 0
    else:
        d = re.sub('\sday','',d[0])
        d = int(d)
        return d
    
def holi(ts,holidays):    
    if ts in holidays:
        return 1
    else:
        return 0


def process_url(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    #print(soup.prettify())
    
    store = soup.find_all(attrs={"id": "dealsList"})[0].section['data-dmt-d-store-name']
    title = soup.title.string
    subtitle = soup.find_all(attrs={"class": "subtitle"})[0].string
    subtitle = re.sub('\s{2}','',subtitle)
    description = soup.find_all(attrs={"name": "description"})[0]['content']
    patt =  r'\w*%\s\w{3}'
    dislist= re.findall(patt,description)
    discount = disnum(dislist)
    len_title = len(title.split())
    len_subtitle = len(subtitle.split())
    len_des = len(description.split())

    time_ago = soup.find_all(attrs={"class": "publish"})[0].string
    n_day_past = pastdays(time_ago)
    now = datetime.datetime.now()
    ts = now - datetime.timedelta(days = n_day_past)
    wk = [0,0,0,0,0,0,0]
    day_of_week = ts.weekday()
    wk[day_of_week] = 1

    cal = USFederalHolidayCalendar()
    holidays = cal.holidays(start='2019-10-01', end='2022-01-31')

    hol = holi(ts,holidays)
    
    medpost = pd.read_csv('med_store.csv').T.values.tolist()[0]
    highpost = pd.read_csv('large_store.csv').T.values.tolist()[0]
    word_features = pd.read_csv('word_features.csv').T.values.tolist()[0]
    idf = pd.read_csv('idf.csv').T.values.tolist()[0]

    low_postnum,med_postnum, high_postnum = 0,0,0
    if store in highpost:
        high_postnum = 1
    elif store in medpost:
        med_postnum = 1
    else:
        low_postnum = 1

    all_text = title + subtitle + description
    text_split = all_text.split()

    tf = []
    for word in word_features:
        tf.append(all_text.count(word)/len(text_split))

    tfidf_value = np.multiply(tf, idf) 

    res = pd.DataFrame([discount,len_title, len_subtitle, len_des, n_day_past,day_of_week, hol])
    wks = pd.DataFrame(wk)
    tfidf_values = pd.DataFrame(tfidf_value)
    postnum = pd.DataFrame([low_postnum, med_postnum, high_postnum])

    result = res.append(wks).append(tfidf_values).append(postnum)
    output = result.T
    output.columns = ['disnum', 'len_title', 'len_subtitle', 'len_desc', 'n_day_past',
           'day_of_week', 'hol', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat',
           'Sun'] + word_features +['low_postnum',
           'med_postnum', 'high_postnum'] 

    return output


#prediction function
def predpct(url):
    output = process_url(url)
    loaded_model = pickle.load(open("model.pkl","rb"))
    DM_pred = xgb.DMatrix(data=output)
    result = loaded_model.predict(DM_pred)
    result = np.round(result)[0]
    nlikes =  int(result)
    
    nsaves = pd.read_csv('nsaves.csv')
    nsaves = nsaves.T.values.tolist()[0]

    pct = round(sum([x <= nlikes for x in nsaves])/len(nsaves) *100)

    return [nlikes,pct]

