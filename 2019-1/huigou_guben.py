import time
import requests
import random
import datetime
import pickle
import re
import os
import pandas as pd

from bs4 import BeautifulSoup
from gevent import spawn, joinall, monkey

"""
回购、股本、以及行情的获取与统计
"""

monkey.patch_all()

HEADERS = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'},
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:63.0) Gecko/20100101 Firefox/63.0'},
]

### 从 http://hk.eastmoney.com/buyback_1.html?code=&sdate=&edate= 获取回购数据 ###

res = []


def download_data(url):
    """ 下载页面源代码数据 """

    html = requests.get(url, headers=random.choice(HEADERS))
    return html.text


def cl_data_one(url):
    """ 根据原数据获得指定数据 """
    html = download_data(url)
    soup = BeautifulSoup(html)
    s = soup.tbody
    for tr in s.find_all('tr'):
        gp = []
        for td in tr.find_all('td'):
            gp.append(td.text.strip())
        yield gp


def cl_data(url):
    """ 根据原数据获得指定数据 """
    for gp in cl_data_one(url):
        res.append(gp)
    time.sleep(0.1)


def get_data():
    """ 获得数据列表 """
    for i in range(1, 845, 3):
        try:
            url1 = f'http://hk.eastmoney.com/buyback_{i}.html?code=&sdate=&edate='
            url2 = f'http://hk.eastmoney.com/buyback_{i+1}.html?code=&sdate=&edate='
            if i == 843:
                joinall([spawn(cl_data, url1), spawn(cl_data, url2)])
                break
            else:
                url3 = f'http://hk.eastmoney.com/buyback_{i+2}.html?code=&sdate=&edate='
                joinall([spawn(cl_data, url1), spawn(cl_data, url2), spawn(cl_data, url3)])
        except Exception as exc:
            print(exc)
        print(i)

    return res


###  从 http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=GJZB&sty=HKF10&code=00298&js=var%20CompanyInfo=[(x)]&_= 获取港股本数据 ###


def hkEQUITY(code):
    """ 获取指定港股代码的港股本 """
    url = f"http://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?type=GJZB&sty=HKF10&code={code}&js=var%20CompanyInfo=[(x)]&_="
    html = requests.get(url, headers=random.choice(HEADERS)).text
    html = eval(html[16:])[0]
    time.sleep(0.1)
    return code, html['HKEQUITY']


def get_HKEQUITY(codes):
    """ 获取指定港股代码列表的港股本字典 """
    hk_equity = []
    len_codes = len(codes)
    for i in range(0, len_codes, 3):
        c1 = spawn(hkEQUITY, codes[i])
        c2 = spawn(hkEQUITY, codes[i + 1])
        c3 = spawn(hkEQUITY, codes[i + 2])
        try:
            [hk_equity.append(jo.get()) for jo in joinall([c1, c2, c3])]
        except Exception as exc:
            print(exc, i)
        print('.....', i)
    if i < len_codes - 1:
        for ic in range(i + 1, len_codes):
            try:
                hk_equity.append(hkEQUITY(codes[ic]))
            except Exception as exc:
                print(exc, ic)
            print('.....', ic)
    return hk_equity


#####################################     更新    #####################################


def get_hkhq(code_str):
    """ 获取指定港股代码集的行情
        temp[0]------CHEUNG KONG------名称
        temp[1]------长和------股票名称
        temp[2]------90.300------今日开盘价
        temp[3]------91.050------昨日收盘价
        temp[4]------91.050------最高价
        temp[5]------90.000------最低价
        temp[6]------90.750------当前价（现价）
        temp[7]------ -0.300------涨跌
        temp[8]------ -0.329------涨幅
        temp[9]------90.650------买一
        temp[10]------90.750------卖一
        temp[11]------627798876------成交额
        temp[12]------6932826------成交量
        temp[13]------2.954------市盈率
        temp[14]------2.810------周息率（2.810%）
        temp[15]------118.800------52周最高
        temp[16]------87.600------52周最低
        temp[17]------2016/06/22------日期
        temp[18]------16:01------时间
    """
    url = 'http://hq.sinajs.cn/list=' + code_str
    html = requests.get(url)
    h = html.text
    comp = re.compile('hq_str_hk(.*?)";')
    h2 = comp.findall(h)
    data = {}
    # ['名称', '股票名称', '今日开盘价', '昨日收盘价', '最高价', '最低价', '当前价（现价）', '涨跌', '涨幅', '买一', '卖一', '成交额', '成交量', '市盈率', '周息率', '52周最高', '52周最低', '日期', '时间']
    for i in h2:
        i2 = i.split('="')
        temp = i2[1].split(',')
        data[i2[0]] = [temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7], temp[8], temp[9],
                       temp[10], temp[11], temp[12], temp[13], temp[14], temp[15], temp[16], temp[17], temp[18]]

    return data


def gengxin(pkl='huigou_guben.pkl'):
    """ 获取pickle文件 """
    data = pd.read_pickle(pkl)
    dates = set(i[0] for i in data)
    this_date = str(datetime.datetime.now())[:10]
    gps = []
    gp_gb = {i[1]: i[8] for i in data[1:]}
    flag = False
    update_date = str(datetime.datetime.fromtimestamp(os.path.getmtime('huigou_guben.pkl')))[:10]  # 获取文件修改日期
    if this_date != update_date and this_date not in dates:
        for i in range(1, 300):
            url = f'http://hk.eastmoney.com/buyback_{i}.html?code=&sdate=&edate='
            for gp in cl_data_one(url):
                if gp[8] in dates:
                    flag = True
                    break
                gps.append([
                    gp[8], gp[1], gp[2],
                    float(gp[3].replace('万', '')) * 10000 if '万' in gp[3] else float(gp[3]),
                    float(gp[4]), float(gp[5]), float(gp[6]),
                    float(gp[7].replace('万', '')) * 10000 if '万' in gp[7] else float(gp[7]),
                    gp_gb[gp[1]]
                ])
            if flag:
                break
        data = data[:1] + gps + data[1:]
        with open(pkl, 'wb') as f:
            f.write(pickle.dumps(data))

    return data


def main():
    data = gengxin()
    codes = {i[1] for i in data[1:]}
    code_str = 'hk' + ',hk'.join(codes)
    data2 = get_hkhq(code_str)
    data3 = {}
    for t, code, name, v, h, l, avg, cou, gb in data[1:]:
        if code not in data3:
            data3[code] = [code, name, v, h, l, avg, cou, gb, 1]
        else:
            data3[code][2] += v
            if h > data3[code][3]:
                data3[code][3] = h
            if l < data3[code][4]:
                data3[code][4] = l
            data3[code][5] += avg
            data3[code][6] += cou
            data3[code][8] += 1

    data4 = [['股票代码', '股票名称', '回购数量(股)', '最高回购价', '最低回购价', '回购平均价', '回购总额(港元)', '港股本', '回购百分比',
              '名称', '股票名称', '今日开盘价', '昨日收盘价', '最高价', '最低价', '当前价（现价）', '涨跌', '涨幅', '买一', '卖一', '成交额',
              '成交量', '市盈率', '周息率', '52周最高', '52周最低', '日期', '时间']]
    for k, v in data3.items():
        v[5] = round(v[5] / v[8], 3)
        v[8] = round(v[2] / v[7] * 100, 3)
        data4.append(v + data2[k])

    return data4


if __name__ == '__main__':
    data = main()
    data = pd.DataFrame(data[1:], columns=data[0])
    print(data)
