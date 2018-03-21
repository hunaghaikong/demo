import pandas as pd
import MyUtil

def get_address_data(address=0):
    ''' 从CSV获取数据 '''
    data=pd.read_csv(address,parse_dates=False,header=None,names=['date','open','high','low','close','vol'])
    data['date']=pd.to_datetime(data.date)
    return data

def get_macd_data(data,short=0,long=0,mid=0):
    if short==0:
        short=12
    if long==0:
        long=26
    if mid==0:
        mid=9
    data['sema']=pd.ewma(data['close'],span=short)
    data['lema']=pd.ewma(data['close'],span=long)
    data.fillna(0,inplace=True)
    data['data_dif']=data['sema']-data['lema']
    data['data_dea']=pd.ewma(data['data_dif'],span=mid)
    data['data_macd']=2*(data['data_dif']-data['data_dea'])
    data.fillna(0,inplace=True)
    return data[['data_dif','data_dea','data_macd']]

def get_kdj_data(data,N=0,M=0):
    if N==0:
        N=9
    if M==0:
        M=2
    low_list=pd.rolling_min(data['low'],N)
    low_list.fillna(value=pd.expanding_min(data['low']),inplace=True)
    high_list=pd.rolling_max(data['high'],N)
    high_list.fillna(value=pd.expanding_max(data['high']),inplace=True)
    rsv=(data['close']-low_list)/(high_list-low_list)*100
    data['kdj_k']=pd.ewma(rsv,com=M)
    data['kdj_d']=pd.ewma(data['kdj_k'],com=M)
    data['kdj_j']=3*data['kdj_k']-2*data['kdj_d']
    data.fillna(0,inplace=True)
    return data[['kdj_k','kdj_d','kdj_j']]

def get_ma_data(data,N=0):
    if N==0:
        N=5
    data['ma']=pd.rolling_mean(data['close'],N)
    data.fillna(0,inplace=True)
    return data[['ma']]

def get_rsi_data(data,N=0):
    if N==0:
        N=24
    data['value']=data['close']-data['close'].shift(1)
    data.fillna(0,inplace=True)
    data['value1']=data['value']
    data['value1'][data['value1']<0]=0
    data['value2']=data['value']
    data['value2'][data['value2']>0]=0
    data['plus']=pd.rolling_sum(data['value1'],N)
    data['minus']=pd.rolling_sum(data['value2'],N)
    data.fillna(0,inplace=True)
    rsi=data['plus']/(data['plus']-data['minus'])*100
    data.fillna(0,inplace=True)
    rsi=pd.DataFrame(rsi,columns=['rsi'])
    return rsi

def get_cci_data(data,N=0):
    if N==0:
        N=14
    data['tp']=(data['high']+data['low']+data['close'])/3
    data['mac']=pd.rolling_mean(data['tp'],N)
    data['md']=0
    for i in range(len(data)-14):
        data['md'][i+13]=data['close'][i:i+13].mad()
    cci=(data['tp']-data['mac'])/(data['md']*0.015)
    cci=pd.DataFrame(cci,columns=['cci'])
    return cci

import numpy as np
import datetime
import time

def macds():
    '''
    :return: macd data,DataFrame format
    '''
    conn=MyUtil.get_conn('stock_data')
    sql="SELECT DATETIME,OPEN,high,low,CLOSE,vol FROM index_min WHERE CODE='HSIc1' LIMIT 0,71773"
    df=pd.read_sql(sql,conn)
    df.columns=['date','open','high','low','close','volume']
    MyUtil.closeConn(conn)
    def get_EMA(df,N):
        for i in range(len(df)):
            if i==0:
                df.ix[i,'ema']=df.ix[i,'close']
            if i>0:
                df.ix[i,'ema']=(2*df.ix[i,'close']+(N-1)*df.ix[i-1,'ema'])/(N+1)
        ema=list(df['ema'])
        return ema
    def get_MACD(df,short=12,long=26,M=9):
        a=get_EMA(df,short)
        b=get_EMA(df,long)
        df['diff']=pd.Series(a)-pd.Series(b)
        #print(df['diff'])
        for i in range(len(df)):
            if i==0:
                df.ix[i,'dea']=df.ix[i,'diff']
            if i>0:
                df.ix[i,'dea']=(2*df.ix[i,'diff']+(M-1)*df.ix[i-1,'dea'])/(M+1)
        df['macd']=2*(df['diff']-df['dea'])
        return df
    return get_MACD(df,12,26,9)

def macd_to_sql(data):
    '''
    :param data: macd data
    :return: None,Write data to the database
    '''
    conn=MyUtil.get_conn('stock_data')
    cur=conn.cursor()
    sql="insert into macd(code,date,open,high,low,close,volume,ema,diff,dea,macd) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    count=0
    for d in data.values:
        try:
            cur.execute(sql,('HSIc1',str(d[0]),d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9]))
            count+=1
            if not count%10000:
                conn.commit()
        except Exception as exc:
            print(exc)
            continue
    conn.commit()
    MyUtil.closeConn(conn)


def main():
    # adds=r'C:\Users\Administrator\Desktop\stockData\000001.day.csv'
    # data=get_address_data(address=adds)
    # macd=get_macd_data(data)
    # kdj=get_kdj_data(data)
    # ma=get_ma_data(data)
    # rsi=get_rsi_data(data)
    # cci=get_cci_data(data)
    # df=macds()
    # print(df)
    pass

if __name__=='__main__':
    main()
    data=macds()
    macd_to_sql(data)