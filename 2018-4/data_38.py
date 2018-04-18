import requests
import json
import h5py
import time
import numpy as np
from sklearn import svm
from sklearn.externals import joblib
import h5py


def getData(size=800):
    # data=requests.get('http://web.ifzq.gtimg.cn/appstock/app/kline/kline?_var=kline_dayqfq&param=%s,day,,,10'%code).text
    # data=json.loads(data.split('=',1)[1])['data'][code]['day']
    # data=[[int(i[0].replace('-','')),float(i[1]),float(i[2])] for i in data]
    # data.reverse()
    # sj=time.localtime(time.time()).tm_hour
    # if 9<sj<15:
    # data=[[data[i][1],data[i][2]] for i in range(1,10)]
    # else:
    #     data=[[data[i][1],data[i][2]] for i in range(9)]
    # data.reverse()
    # d=[]
    # for i in data:
    #      d.append(i[0])
    #      d.append(i[1])
    h5 = h5py.File(r'D:\tools\Tools\stock_data.hdf5', 'r')
    d = None
    while 1:
        code = yield d
        if code == 'stop':
            break
        try:
            d = h5['stock/%s.day' % code][-size:]
        except:
            d = None

    h5.close()

    #return d


def getCode():
    with open('codes_gp.txt') as f:
        codes = f.read()
    codes = codes.split(',')
    return codes[:-1]


def main(ts=9,interval=1,rose=0.099):
    ''' ts:默认9天，interval:涨跌比较间隔默认1天，rose:涨跌幅度默认0.099 '''
    codes = getCode()
    errors = 0
    data_result = []
    h5 = h5py.File('datas.hdf5', 'w')
    data = None
    get_data = getData()
    get_data.send(None)
    for code in codes:
        try:
            data = get_data.send(code)
        except Exception as exc:
            print(exc, code)
            errors += 1
            if errors > 10:
                break
            continue
        if data is None:
            continue
        for i in range(ts, len(data)):
            zf = (data[i][4] - data[i - interval][4]) / data[i - interval][4]
            jieguo = []
            for j in range(i - ts, i):
                jieguo.append(float(data[j][1]))
                jieguo.append(float(data[j][4]))
            if zf >= rose:
                jieguo.append(1)
            else:
                jieguo.append(0)
            data_result.append(jieguo)
    h5['datas'] = data_result
    h5.close()

def main5():
    codes = getCode()
    errors = 0
    data_result = []
    h5 = h5py.File('datas5.hdf5', 'w')
    data = None
    get_data = getData()
    get_data.send(None)
    for code in codes:
        try:
            data = get_data.send(code)
        except Exception as exc:
            print(exc, code)
            errors += 1
            if errors > 10:
                break
            continue
        if data is None:
            continue
        for i in range(14, len(data)):
            zf = (data[i][4] - data[i - 5][4]) / data[i - 5][4]
            jieguo = []
            for j in range(i - 14, i-5):
                jieguo.append(float(data[j][1]))
                jieguo.append(float(data[j][4]))
            if zf >= 0.3:
                jieguo.append(1)
            else:
                jieguo.append(0)
            data_result.append(jieguo)
    h5['datas5'] = data_result
    h5.close()


def yanzen():
    '''模型验证'''
    clf = joblib.load('gupiao.m')
    codes = getCode()
    co = 0
    zt = []
    dict_data = {}
    for code in codes:
        try:
            data = getData(code)
            dict_data[code] = data.copy()
        except Exception as exc:
            print(exc, code)
            continue
        co += 1
        jg = clf.predict([data])[0]
        if jg > 0:
            print(code)
            zt.append(code)
    print(co)
    with open('dict_data%s.txt' % str(time.localtime()[1:3]), 'w') as f:
        f.write(json.dumps(dict_data))
    return zt


if __name__ == '__main__':
    # yanzen()
    main()
