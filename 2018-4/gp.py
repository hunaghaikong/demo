import json
import h5py
import time
import os
from struct import unpack
from datetime import datetime
import importlib, asyncio
import numpy as np
import threading
from sklearn.externals import joblib
from collections import Counter
import multiprocessing
import random
import re
import sys

# 支持向量机，决策树，K最近邻，随机森林
from sklearn import svm, tree, neighbors, ensemble

"""
股票
"""

class BaseHdf(object):
    def __init__(self,fol=r'D:\tools\Tools',ts=10):
        self.thread_size = 30  # 30个线程
        self.base_file = fol+os.sep+'stock_data.hdf5' if fol else 'stock_data.hdf5' # 存储股票日线数据的文件
        self.f_base = None
        self.ts=ts  # 天数
        # 通达信的二进制文件存储路径
        self.folder_tdx = ['D:\\新建文件夹\\vipdoc\sz\\lday', 'D:\\新建文件夹\\vipdoc\\sh\\lday']
        #self.folder_tdx = ['C:\\通达信\\new_tdx\\vipdoc\sz\\lday', 'C:\\通达信\\new_tdx\\vipdoc\\sh\\lday']

    def dateformat(self,a):
        ''' 格式化日期 '''
        y = int(a / 10000)
        m = int((a % 10000) / 100)
        d = int((a % 10000) % 100)
        dt = y * 100
        dt += m
        dt *= 100
        dt += d
        return dt

    def day_hdf_data(self,dirname, fname):
        ''' 全部写入hdf5文件 '''
        if self.f_base==None:
            return
        ofile = open(dirname + os.sep + fname, 'rb')
        buf = ofile.read()
        e = 0
        result = []
        while 1:
            try:
                a = unpack('IIIIIfII', buf[e:e + 32])
                if not a:
                    break
                dd = self.dateformat(a[0])
            except Exception as exc:
                print(exc)
                break
            openPrice = a[1] / 100.0
            high = a[2] / 100.0
            low = a[3] / 100.0
            close = a[4] / 100.0
            amount = a[5]
            vol = a[6]
            e += 32
            result.append([dd, openPrice, high, low, close, amount, vol])

        self.f_base['/stock/%s' % fname] = result
        ofile.close()
        print(fname)

    def day_data_10(self,dirname, fname):
        if self.f_base==None:
            return
        ts=self.ts
        ofile = open(dirname + os.sep + fname, 'rb')
        buf = ofile.read()
        e = (len(buf)//32-ts)*32
        result=[]
        
        for is_10 in range(ts):
            try:
                a = unpack('IIIIIfII', buf[e:e+32])
                if not a or len(a)<7:
                    break
                dd = self.dateformat(a[0])
            except Exception as exc:
                print(exc)
                break
            
            openPrice = a[1] / 100.0
            high = a[2] / 100.0
            low = a[3] / 100.0
            close = a[4] / 100.0
            amount = a[5]
            vol = a[6]   
            e += 32
            #print(dd, openPrice, high, low, close, amount, vol,fname)
            result.append([dd, openPrice, high, low, close, amount, vol])

        if result:
            self.f_base['/stock/%s' % fname]=result.copy()
        ofile.close()
        print(fname)

    def thread_func(self,func,path, file_name, x):
        ''' 多线程 '''
        threads = [threading.Thread(target=func, args=(path, i)) for i in file_name[x:x + self.thread_size]]
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()

    def main_setHdf(self):
        ''' 把股票日线数据写入hdf5文件 '''
        t1=time.localtime()
        t2=time.localtime(os.path.getmtime(self.base_file))
        if t1.tm_mday==t2.tm_mday and t1.tm_hour==t2.tm_hour:
            return        
        self.f_base = h5py.File(self.base_file, 'w')  # 要写入股票日线数据的文件
        if isinstance(self.ts,int):
            func=self.day_data_10
        else:
            func=self.day_hdf_data
        path = self.folder_tdx
        thread_size=self.thread_size
        try:
            for p in range(len(path)):
                x = 0
                file_name = [i for i in os.listdir(path[p])]
                file_count = int(len(file_name) / thread_size) - 1
                file_yu = len(file_name) % thread_size
                for fn in range(file_count):
                    self.thread_func(func,path[p], file_name, x)
                    x += thread_size
                self.thread_func(func,path[p], file_name, x + file_yu)
        except Exception as exc:
            print(exc)
        finally:
            self.f_base.close()

class Gupiao(object):
    def __init__(self,fol=r'D:\tools\Tools'):
        self.fl={
            'md_folder':'models', # 存储模型的文件夹
            'code':'codes_gp.txt', # 股票代码文件
            'base':fol+os.sep+'stock_data.hdf5' if fol else 'stock_data.hdf5', # 存储股票日线数据的文件
            'train':'datas.hdf5', # 存储处理好可供学习的数据
            '_data':'dict_data.txt', # 存储要将要预测的数据
        }
        # 涨停股票更新的时间
        self.this_date = []
        with open(self.fl['code']) as f:
            codes = f.read()
        self.codes = codes.replace('\n', ',').split(',')[:-1]

    def get_model(self,mn):
        ''' 获取实例化的模型 '''
        if mn == 'svm':
            return svm.SVC()
        if mn == 'tree':
            return tree.DecisionTreeClassifier()
        if mn == 'neighbors':
            return neighbors.KNeighborsClassifier(n_neighbors=15, weights='uniform')
        if mn == 'rfcf':
            return ensemble.RandomForestClassifier(n_estimators=8)
        return None

    def data_storage(self,ts=9,interval=1,rose=0.099,size=800):
        ''' 存储数据供训练用
        ts:默认9天，interval:涨跌比较间隔默认1天，rose:涨跌幅度默认0.099,size:单个股票最近日线数据条数 '''

        # 读取hdf5数据
        h5_r = h5py.File(self.fl['base'], 'r')
        data_result = []

        data = None
        for code in self.codes:
            try:
                data = h5_r['stock/%s.day' % code][-size:]
            except Exception as exc:
                print(exc, code)
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

        h5_r.close()
        h5_w = h5py.File(self.fl['train'], 'w')
        h5_w['datas'] = data_result
        h5_w.close()

    def model_train(self,md_name='tree',size=120000):
        '''训练模型。
        md_name:模型名称有：svm(支持向量机),tree(决策树),neighbors(K最近邻),rfcf(随机森林)
        size:未达上涨条件的数据量
        '''
        h5 = h5py.File(self.fl['train'],'r')
        d = h5['datas'][:]
        h5.close()
        d1=d[np.where(d[:,-1]==1)]
        d2=d[np.where(d[:,-1]==0)]
        random.shuffle(d2)
        d3=list(d1)+list(d2[:size])
        random.shuffle(d3)
        d3=np.array(d3)
        md=self.get_model(md_name)
        lens=len(d3[0])
        if not os.path.isdir(self.fl['md_folder']):
            os.makedirs(self.fl['md_folder'])
        if md:
            md.fit(d3[:, :-1], d3[:, -1])
            joblib.dump(md, self.fl['md_folder']+os.sep+md_name+str(lens)+'.m')

    def get_h5py_data(self,size=9):
        ''' 从存储股票日线数据的文件获取数据'''
        data = {}
        h5 = h5py.File(self.fl['base'], 'r')
        aaa = 0

        for code in self.codes:
            try:
                d = h5['/stock/%s.day' % code][-size:]
            except:
                continue

            if aaa % 300 == 0:
                self.this_date.append(d[-1][0])
                print(d[-1][0], code)
            aaa += 1
            d1 = []
            for d2 in d:
                d1.append(float(d2[1]))
                d1.append(float(d2[4]))
            data[code] = d1.copy()
        h5.close()
        te = Counter(self.this_date)
        te = str(te.most_common(1)[0][0])
        self.this_date = te[:4] + '-' + te[4:6] + '-' + te[6:8]
        data["last_date"] = te[:8]
        with open(self.fl['_data'], 'w') as f:
            f.write(json.dumps(data))
        return data

    def yuce(self, data, mod, mod_name):
        ''' 预测 '''
        mx_n = []
        # k=['bayes', 'logisRgs', 'lrgs', 'mlpcf', 'ngbs', 'rfcf', 'svms', 'trees']
        jg = []

        co = 0
        for code in self.codes:
            if not data.get(code):
                continue
            if len(data[code])<18:
                continue
            r = mod.predict([data[code]])[0]
            if r == 1:
                jg.append(code)
                mx_n.append(code)
            co += 1
        return jg, mx_n, mod_name, co

    def main_yc(self):
        ''' 预测最终要调用的方法 '''
        pool = multiprocessing.Pool(processes=3)  # 进程数3
        result = []
        data = self.get_h5py_data()
        zt = []
        mx_n = {}
        for m in os.listdir(self.fl['md_folder']):
            mod = joblib.load(self.fl['md_folder']+os.sep+ m)
            mx_n[m[:-2]] = []
            result.append(pool.apply_async(self.yuce, (data, mod, m[:-2])))
        pool.close()
        pool.join()
        for res in result:
            jg, mx_ns, mod_name, co = res.get()
            zt += jg
            mx_n[mod_name] = mx_ns
            print(co)
        
        zt = Counter(zt)
        zt = zt.most_common(12)
        return zt, mx_n

if __name__=='__main__':
    gpw=BaseHdf('')
    gp=Gupiao('')
    gpw.main_setHdf()
    zt,mx_n=gp.main_yc()
    zt1=[i[0] for i in zt]
    zzzt=[zt1[0]]
    zzzt.append(random.choice(zt1[1:]))
    te=gp.this_date
    dict_zt={}
    try:
        with open('jyzt_gp.txt','r') as f:
            dict_zt=json.loads(f.read())
    except:
        pass
    with open('jyzt_gp.txt','w') as f:
        f.write(json.dumps(dict({te:zt[:10]},**dict_zt)))
    xzs=len(sys.argv)>1
    if xzs:
        print(zt)
    else:
        print(zzzt)
    for i in mx_n:
        if xzs:
            print(i,mx_n[i])
            continue
        r=re.findall('.*?score(\d\d\d|\d\d|\d)',i)
        try:
            if r and int(r[0])>90:
                print(i,mx_n[i])
        except:
            continue

