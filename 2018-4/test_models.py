import pymysql
import numpy as np
import h5py
import os
from struct import unpack
from datetime import datetime
from sklearn.externals import joblib
from collections import Counter
from threading import Thread
import multiprocessing


class My_test():
    def __init__(self):
        self.path = ['D:\\新建文件夹\\vipdoc\sz\\lday', 'D:\\新建文件夹\\vipdoc\\sh\\lday']
        self.codes=[]
        #self.h5 = h5py.File('stock_data.hdf5')
        for i in self.path:
            self.codes+=os.listdir(i)

    def dateformat(self,a):
        y = int(a / 10000)
        m = int((a % 10000) / 100)
        d = int((a % 10000) % 100)
        dt=y*100
        dt+=m
        dt*=100
        dt+=d
        return dt

    def day_data_10(self, dirname,fname,qj):
        ofile = open(dirname + os.sep + fname, 'rb')
        buf = ofile.read()
        qj1=qj+10
        e = (len(buf)//32-qj1)*32
        if e<0:
            return
        result=[]
        
        for is_10 in range(10):
            try:
                a = unpack('IIIIIfII', buf[e:e+32])
                if not a or len(a)<7:
                    break
                dd = self.dateformat(a[0])
            except Exception as exc:
                #print(exc)
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
        
        #print(np.array(result))
        # if result:
        #     del self.h5['/stock/%s' % fname]
        #     self.h5['/stock/%s' % fname]=result.copy()
        #f['/stock/%s' % fname[3:-4]]=result
        #f['/stock/%s' % fname] =result
        ofile.close()
        return result

    def get_h5py_data(self):
        zt=[]
        data={}
        aaa=0
        while 1:
            qj=yield (data,zt)
            for dirname in self.path:
                for code in os.listdir(dirname):
                    try:
                        d = self.day_data_10(dirname=dirname,fname=code,qj=qj)
                        if not d or d and len(d)<10:
                            continue
                    except Exception as exc:
                        print(exc)
                        continue
                    if aaa%300==0:
                        print (d[-1][0],code)
                    aaa+=1
                    d1=[]
                    for d2 in d:
                        d1.append(float(d2[1]))
                        d1.append(float(d2[4]))
                    #print(d1)
                    if len(d1)==20:
                        if (d1[19]-d1[17])/d1[17]>=0.099:
                            zt.append(code)
                        data[code]=d1[:18].copy()
        

    def yuce(self,data,zt,mod,mod_name):
        mx_n=[]
        mx_zt=0
        mx_sum=0
        # for m in os.listdir('test_models'):
        #     mx[m[:-2]]=joblib.load('test_models\\'+m)
        #     mx_n[m[:-2]]=[]
        #     mx_zt[m[:-2]]=0
        #     mx_sum[m[:-2]]=0

        #k=['bayes', 'logisRgs', 'lrgs', 'mlpcf', 'ngbs', 'rfcf', 'svms', 'trees']
        
        co=0
        
        for code in self.codes:
            if not data.get(code):
                continue
            r=mod.predict([data[code]])[0]
            if r==1:
                mx_n.append(code)
                mx_sum+=1
                if code in zt:
                    mx_zt+=1
            co+=1
            #for i in mx.keys():
            #    for j in mx_n[i]:
            #        if j in zt:
            #            mx_zt[i]+=1
                
        
        return mx_zt,mx_sum,mod_name,co

    def main(self):
        si_qj=16    # 测试天数15
        pool=multiprocessing.Pool(processes=3)   # 进程数3
        model_dir='test_models' # 要测试的文件夹名称
        mx_n={}
        mx_zt={}
        mx_sum={}
        result=[]
        ghd=self.get_h5py_data()
        ghd.send(None)
        # 加载模型
        xl_count=0
        for m in os.listdir(model_dir):
            if 'score' in m:
                continue
            xl_count+=1
            mod=joblib.load(model_dir+os.sep+m)
            mx_n[m[:-2]]=[]
            mx_zt[m[:-2]]=0
            mx_sum[m[:-2]]=0
            for v_10 in range(1,si_qj):
                data,zt=ghd.send(v_10)
                result.append(pool.apply_async(self.yuce,(data,zt,mod,m[:-2])))
        pool.close()
        pool.join()
        for res in result:
            mx_zts,mx_sums,mod_name,co=res.get()
            mx_zt[mod_name]+=mx_zts
            mx_sum[mod_name]+=mx_sums
            print(co)
            
        
        for i in mx_zt.keys():
            if mx_sum[i]>0:
                score=mx_zt[i]/mx_sum[i]*100
            else:
                score=0
            print(i,mx_zt[i],mx_sum[i],'分数：%s'%score)
            try:
                # 更改模型名称并写上得分
                os.rename(model_dir+os.sep+i+'.m',model_dir+os.sep+i+'-score'+str(round(score))+'.m')
            except Exception as exc:
                print(exc)

        if xl_count==0:
            print('没有要测试的模型！')

if __name__=='__main__':
    gp=My_test()
    gp.main()
