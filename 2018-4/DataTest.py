import pymysql
import pandas as pd
import numpy as np
import os

from AndBefore_2018_3 import MyUtil

class Data:
    def ohlcf(self,x):
        if x.h1 and not x.h2:
            return [x.open, x.high, x.low, x.close, x.open2, x.high2, x.low2, x.close2, x.h1, x.h2, x.o, x.h, x.l, x.c]
        elif x.h2 and not x.h1:
            return [x.open2, x.high2, x.low2, x.close2, x.open, x.high, x.low, x.close, x.h1, x.h2, x.o, x.h, x.l, x.c]
        elif x.h1 and x.h2:
            if x.open == x.high == x.low == x.close:
                return [x.open2, x.high2, x.low2, x.close2, x.open, x.high, x.low, x.close, x.h1, x.h2, x.o, x.h, x.l,x.c]
            else:
                h = x.high if x.high > x.high2 else x.high2
                l = x.low if x.low < x.low2 else x.low2
                return [x.open, h, l, x.close, x.open2, x.high2, x.low2, x.close2, x.h1, x.h2, x.o, x.h, x.l, x.c]
        else:
            return [x.open, x.high, x.low, x.close, x.open2, x.high2, x.low2, x.close2, x.h1, x.h2, x.o, x.h, x.l, x.c]

    def get_data(self,conn):
        #sql="SELECT datetime,open,high,low,close FROM stock_data.index_min WHERE CODE='HSIc1' AND DATE_FORMAT(DATETIME,'%Y-%m-%d')='{}'".format(dt)
        #sql2="SELECT datetime,open,high,low,close FROM carry_investment.futures_min WHERE DATE_FORMAT(DATETIME,'%Y-%m-%d')='{}'".format(dt)

        sql="SELECT datetime,open,high,low,close FROM stock_data.index_min WHERE CODE='HSIc1'"
        sql2="SELECT datetime,open,high,low,close FROM carry_investment.futures_min"

        _data=pd.read_sql(sql,conn)
        _data.index=_data.datetime
        _dt=list(set(_data.index.strftime("%Y-%m-%d")))

        _data3=pd.read_sql(sql2,conn)
        _data3.index=_data3.datetime
        _dt3=list(set(_data3.index.strftime("%Y-%m-%d")))

        _dt=list(set(_dt+_dt3))
        _dt.sort()

        for dt in _dt:
            data=_data[_data.index.strftime("%Y-%m-%d")==dt]
            data3=_data3[_data3.index.strftime("%Y-%m-%d")==dt]
            p=pd.date_range(start='{} 00:00'.format(dt),periods=1440,freq='60s')
            if len(data3)>0:
                ind=data3[data3.index.second!=0]
                if len(ind)>0:
                    ind=ind.index
                    ind2=set((i.hour,i.minute) for i in ind)
                    for i in ind2:
                        try:
                            dd=data3[(data3.index.hour==i[0])&(data3.index.minute==i[1])]
                            t=dd.index[0]
                            t=str(t)[:-2]+'00'
                            t=pd.Timestamp.strptime(t,"%Y-%m-%d %X")
                            if len(dd)>1:
                                ohlc=[dd.open[0],dd.high.max(),dd.low.min(),dd.close[-1]]
                            else:
                                ohlc=dd.values[0]
                            data3=data3.drop(dd.index)
                            data3.loc[t]=ohlc
                            data3=data3.sort_index()
                        except Exception as exc:
                            print(exc)


            #data1=pd.DataFrame(np.zeros((1440,4)),columns=data.columns,index=p)
            data1=pd.DataFrame([[i,0,0,0,0] for i in p],columns=data.columns,index=p)

            data2=pd.DataFrame({'datetime':p})
            data2.index=data2.datetime

            data=data.loc[:,['open','high','low','close']]+data1.loc[:,['open','high','low','close']]
            #data=data.fillna(0)

            data3=data3.loc[:,['open','high','low','close']]+data1.loc[:,['open','high','low','close']]
            #data3=data3.fillna(0)


            data3.columns=['open2','high2', 'low2','close2']
            data5=pd.concat([data,data3],axis=1)

            ix=['open','high','low','close','open2','high2', 'low2','close2']
            data5=data5.ix[:,ix]

            #data5.datetime=data5.index

            da=data5.assign(h1=lambda x:x.high>0,h2=lambda x:x.high2>0,o=lambda x:x.open==x.open2,h=lambda x:x.high==x.high2,l=lambda x:x.low==x.low2,c=lambda x:x.close==x.close2)
            ix=['open', 'high', 'low', 'close', 'open2', 'high2', 'low2', 'close2', 'h1', 'h2', 'o', 'h', 'l','c']
            da=da.ix[:,ix]

            yield da

    def data(self):
        conn = MyUtil.get_conn('stock_data')
        da=pd.DataFrame()
        das=self.get_data(conn)
        try:
            for d in das:
                da=pd.concat((da,d),axis=0)
        finally:
            conn.close()
        return da

    def ohlc(self):
        da=self.data()
        da=da.fillna(0)
        da=da.apply(self.ohlcf,1)
        da=da.ix[:,['open','high','low','close']]
        return da

    def insertSql(da,conn=None,sql=None):
        if not conn:
            conn=MyUtil.get_conn('stock_data')
        cur=conn.cursor()
        if not sql:
            sql="INSERT INTO handle_min(datetime,open,high,low,close) values(%s,%s,%s,%s,%s)"

        #从数据库查询最大更新时间
        #cur.execute('select max(datetime) from handle_min')
        #max_dt=cur.fetchall()[0][0]

        for k,v in zip(da.index,da.values):
            cur.execute(sql,(str(k),float(v[0]),float(v[1]),float(v[2]),float(v[3])))
        conn.commit()
