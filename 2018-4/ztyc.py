import h5py
import os
from sklearn.externals import joblib
from collections import Counter
import multiprocessing
import random
import re
import sys
import json

this_date=[]

class Gpyc():
    def __init__(self):
        with open('codes_gp.txt', 'r') as f:
            codes = f.read()
        self.codes=codes.replace('\n',',').split(',')[:-1]

    def get_h5py_data(self):
        # conn=pymysql.connect(host='',user='',passwd='',charset='utf8',port=3306,db='stock_data')
        # cur=conn.cursor()
        # cur.execute('SELECT `date` FROM transaction_data GROUP BY `date` ORDER BY `date` DESC LIMIT 8,1')
        # dates=str(cur.fetchall()[0][0])[:10]
        # cur.execute(f"SELECT `date`,`open`,`close`,`code` FROM transaction_data WHERE `date`>={dates} AND (`code` LIKE '%sz%' OR `code` LIKE '%sh%')")
        # data=cur.fetchall()
        # conn.close()
        global this_date
        data={}
        h5 = h5py.File(r'D:\tools\Tools\stock_data.hdf5','r')
        aaa=0
        for code in self.codes:
            try:
                d=h5['/stock/%s.day'%code][-9:]
            except:
                continue

            if aaa%300==0:
                this_date.append(d[-1][0])
                print (d[-1][0],code)
            aaa+=1
            d1=[]
            for d2 in d:
                d1.append(float(d2[1]))
                d1.append(float(d2[4]))
            data[code]=d1.copy()
        h5.close()
        te=Counter(this_date)
        te=str(te.most_common(1)[0][0])
        this_date=te[:4]+'-'+te[4:6]+'-'+te[6:8]
        data["last_date"]=te[:8]
        with open('dict_data.txt','w') as f:
            f.write(json.dumps(data))
        return data

    def get_data(self):
        with open('dict_data%s.txt'%str(time.localtime()[1:3]), 'r') as f:
            d = json.loads(f.read())
        return d

    def yuce(self,data,mod,mod_name):
        mx_n=[]
        #k=['bayes', 'logisRgs', 'lrgs', 'mlpcf', 'ngbs', 'rfcf', 'svms', 'trees']
        jg=[]
        
        co=0
        for code in self.codes:
            if not data.get(code):
                continue
            r=mod.predict([data[code]])[0]
            if r==1:
                jg.append(code)
                mx_n.append(code)
            co+=1
        return jg,mx_n,mod_name,co

    def main(self):
        pool=multiprocessing.Pool(processes=3) # 进程数3
        result=[]
        data=self.get_h5py_data()
        zt=[]
        
        mx_n={}
        for m in os.listdir('models'):
            mod=joblib.load('models\\'+m)
            mx_n[m[:-2]]=[]
            result.append(pool.apply_async(self.yuce,(data,mod,m[:-2])))
        pool.close()
        pool.join()
        for res in result:
            jg,mx_ns,mod_name,co=res.get()
            zt+=jg
            mx_n[mod_name]=mx_ns
            print(co)
        zt=Counter(zt)
        zt=zt.most_common(12)
        return zt,mx_n

def tensor(cla):
    '''深度学习'''
    jg=[]
    h5 = h5py.File(r'D:\tools\Tools\stock_data.hdf5','r')
    with open('codes_gp.txt', 'r') as f:
        codes = f.read()
    codes=codes.replace('\n',',').split(',')[:-1]
    aaa=0
    data={}
    for code in codes:
        try:
            d=h5['/stock/%s.day'%code][-9:]
        except:
            continue

        if aaa%300==0:
            print (d[-1][0],code)
        aaa+=1
        d1=[]
        for d2 in d:
            d1.append(float(d2[1]))
            d1.append(float(d2[4]))
        data[code]=d1.copy()
    h5.close()
    co=0
    for code in codes:
        if not data.get(code):
            continue
        r=list(cla.predict(np.array([data[code]])))[0]
        if r==1:
            jg.append(code)
            
        co+=1
    print(co)
    print(jg)
    
    #return jg,mx_n,mod_name,co
    

if __name__=='__main__':
    gp=Gpyc()
    zt,mx_n=gp.main()
    zt1=[i[0] for i in zt]
    zzzt=[zt1[0]]
    zzzt.append(random.choice(zt1[1:]))
    te=this_date
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
