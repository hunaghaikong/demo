import pandas as pd
import numpy as np
import datetime
import time

import MyUtil

def get_data(dates):
    conn=MyUtil.get_conn('stock_data')
    #for i in range(9):
    #dates=dates[:8]+str(int(dates[-2:])+i)
    sql="SELECT datetime,open,high,low,close,vol FROM index_min WHERE code='HSIc1' AND DATE_FORMAT(datetime,'%Y-%m-%d')='{}'".format(dates)
    df=pd.read_sql(sql,conn)
    df.columns=['date','open','high','low','close','vol']
    return df
    MyUtil.closeConn(conn)



def macds(ma=6):
    '''
    :return: macd data,DataFrame format
    '''
    conn=MyUtil.get_conn('stock_data')
    sql="SELECT DATETIME,open,high,low,CLOSE,vol FROM index_min WHERE CODE='HSIc1' AND datetime>'2018-03-12' AND datetime<'2018-03-15'" # LIMIT 0,71773"
    df=pd.read_sql(sql,conn)
    df.columns=['date','open','high','low','close','vol']
    MyUtil.closeConn(conn)
    def get_EMA(df,N):
        for i in range(len(df)):
            if i==0:
                df.ix[i,'ema']=df.ix[i,'close']
            if i>0:
                df.ix[i,'ema']=(2*df.ix[i,'close']+(N-1)*df.ix[i-1,'ema'])/(N+1)
        ema=list(df['ema'])
        return ema
    def get_MACD(df,short=13,long=27,M=10):
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
        df['ma']= df.close.rolling(ma).mean() # pd.rolling_mean(df['close'],ma)
        df['var']=df.close.rolling(ma).var() # pd.rolling_var(df['close'],ma)
        df['std']=df.close.rolling(ma).std() # pd.rolling_std(df['close'],ma)
        df['reg']=0
        df['mul']=0
        co=1 if df.macd[1]>=0 else 0
        for i in range(1,len(df.macd)):
            if df.macd[i]>=0 and df.macd[i-1]<0:
                co+=1
            elif df.macd[i]<0 and df.macd[i-1]>=0:
                co+=1
            df.ix[i,'reg']=co
            price=df.close[i]-df.open[i]
            std=df['std'][i]
            if std is not np.nan:
                df.ix[i, 'mul']=round(price/std,1)

        return df
    return get_MACD(df,12,26,9)

def macd2(df,ma=6,short=13,long=27):

    data=df.close
    df['ema_short']=0
    df['ema_long']=0
    df['diff']=0
    df['dea']=0
    df['macd']=0
    df['ma']= 0
    df['var']=0
    df['std']=0
    df['reg']=0
    df['mul']=0
    co=0
    for i in range(len(data)):
        if i == 1:
            ac = data[i - 1]
            this_c = data[i]
            df.ix[i,'ema_short'] = ac + (this_c - ac) * 2 / short
            df.ix[i,'ema_long'] = ac + (this_c - ac) * 2 / long
            df.ix[i,'diff'] = df.ix[i,'ema_short'] - df.ix[i,'ema_long']
            df.ix[i,'dea'] = df.ix[i,'diff'] * 2 / 10
            df.ix[i,'macd'] = 2 * (df.ix[i,'diff'] - df.ix[i,'dea'])
            co=1 if df.ix[i,'macd']>=0 else 0
        elif i>1:
            n_c = data[i]
            df.ix[i,'ema_short'] = df.ix[i-1,'ema_short'] * 11 / short + n_c * 2 / short
            df.ix[i,'ema_long'] = df.ix[i-1,'ema_long'] * 25 / long + n_c * 2 / long
            df.ix[i,'diff'] = df.ix[i,'ema_short'] - df.ix[i,'ema_long']
            df.ix[i,'dea'] = df.ix[i-1,'dea'] * 8 / 10 + df.ix[i,'diff'] * 2 / 10
            df.ix[i,'macd'] = 2 * (df.ix[i,'diff'] - df.ix[i,'dea'])

        if i>=ma-1:
            df.ix[i,'ma']=sum(data[j] for j in range(i-ma+1,i+1))/ma # 移动平均值
            df.ix[i,'var']=sum((data[j]-df.ix[i,'ma'])**2 for j in range(i-ma+1,i+1))/ma # 方差
            df.ix[i,'std']=np.sqrt(df.ix[i,'var']) # 标准差

        if i>0:
            if df.macd[i]>=0 and df.macd[i-1]<0:
                co+=1
            elif df.macd[i]<0 and df.macd[i-1]>=0:
                co+=1
            df.ix[i,'reg']=co
            price=df.close[i]-df.open[i]
            std=df['std'][i]
            if std is not np.nan:
                df.loc[i, 'mul']=round(price/std,1)

    data=None
    while 1:
        data=yield df[-1:]
        ind=df.shape[0]
        if isinstance(data,list):
            #for i in range(ma-1,ma-1+len(data)):
            #n_c = float(data[5]) ############################'date','open','high','low','close','vol'
            df.ix[ind,'date']=data[0]  # datetime.datetime.strptime(data[0]+' '+data[1],'%Y-%m-%d %H:%M:%S')
            df.ix[ind,'open']=data[1]
            df.ix[ind,'high']=data[2]
            df.ix[ind,'low']=data[3]
            df.ix[ind,'close']=data[4]
            df.ix[ind,'vol']=data[5]

            df.ix[ind,'ema_short'] = df.ix[ind-1,'ema_short'] * 11 / short + df.ix[ind,'close'] * 2 / short  # 当日EMA(12)
            df.ix[ind,'ema_long'] = df.ix[ind-1,'ema_long'] * 25 / long + df.ix[ind,'close'] * 2 / long  # 当日EMA(26)
            df.ix[ind,'diff'] = df.ix[ind,'ema_short'] - df.ix[ind,'ema_long']
            df.ix[ind,'dea'] = df.ix[ind-1,'dea'] * 8 / 10 + df.ix[ind,'diff'] * 2 / 10
            df.ix[ind,'macd'] = 2 * (df.ix[ind,'diff'] - df.ix[ind,'dea'])

            df.ix[ind,'ma']=sum(df.ix[ind-j,'close'] for j in range(ma))/ma # 移动平均值
            df.ix[ind,'var']=sum((df.ix[ind-j,'close']-df.ix[ind,'ma'])**2 for j in range(ma))/ma # 方差
            df.ix[ind,'std']=np.sqrt(df.ix[ind,'var']) # 标准差

            if df.macd[ind]>=0 and df.macd[ind-1]<0:
                co+=1
            elif df.macd[ind]<0 and df.macd[ind-1]>=0:
                co+=1
            df.ix[ind,'reg']=co
            price=df.close[ind]-df.open[ind]
            std=df['std'][ind]
            if std is not np.nan:
                df.ix[ind, 'mul']=round(price/std,1)



def macd_to_sql(data):
    '''
    :param data: macd data
    :return: None,Write data to the database
    '''
    conn=MyUtil.get_conn('stock_data')
    cur=conn.cursor()
    sql="insert into macd(code,date,open,high,low,close,vol,ema,diff,dea,macd,ma,var,std,reg,mul) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    count=0
    data=data.fillna(0)
    for d in data.values:
        try:
            cur.execute(sql,('HSIc1',str(d[0]),d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10],d[11],d[12],d[13],d[14]))
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

def main2(_ma=9,_dates='2018-03-12', _ts=9):
    res={}
    is_d=0
    is_k=0
    i=0
    while i<_ts:
        dates=str(datetime.datetime.strptime(_dates,'%Y-%m-%d')+datetime.timedelta(days=i))[:10]
        df=get_data(dates)
        if len(df)<1:
            i+=1
            continue
        res[dates]={'duo':0,'kong':0,'mony':0,'datetimes':[],'dy':0,'xy':0}
        if i==0:
            data2=macd2(df=df[:_ma+1],ma=_ma)
            dt2=data2.send(None)
        str_time1=None if is_d==0 else str_time1
        str_time2=None if is_k==0 else str_time2
        jg_d=0 if is_d==0 else jg_d
        jg_k=0 if is_k==0 else jg_k
        i+=1
        for df2 in df[_ma+1:].values:
            # df2格式：[Timestamp('2018-03-16 09:22:00') 31304.0 31319.0 31295.0 31316.0 275]
            dt2=data2.send(list(df2))
            dt2=np.array(dt2)[0]
            datetimes,clo,macd,mas,std,reg,mul=dt2[0],dt2[4],dt2[10],dt2[11],dt2[13],dt2[14],dt2[15]
            if mul>1.5:
                res[dates]['dy']+=1
            if mul<-1.5:
                res[dates]['xy']+=1
            if clo>mas and mul>1.5 and is_d==0:
                res[dates]['duo']+=1
                jg_d=clo
                str_time1=str(datetimes)[11:]
                is_d=1
            if clo<mas and mul<-1.5 and is_k==0:
                res[dates]['kong']+=1
                jg_k=clo
                str_time2=str(datetimes)[11:]
                is_k=-1
            if is_d==1 and macd<0 and clo<mas:
                res[dates]['mony']+=(clo-jg_d)
                res[dates]['datetimes'].append([str_time1+'--'+str(datetimes)[11:],'多',clo-jg_d])
                is_d=0
            if is_k==-1 and macd>0 and clo>mas:
                res[dates]['mony']+=(jg_k-clo)
                res[dates]['datetimes'].append([str_time2+'--'+str(datetimes)[11:],'空',jg_k-clo])
                is_k=0

    zje=0
    for i in res:
        print('标准差大于收盘价1.5倍：',res[i]['dy'],'\t','标准差小于收盘价1.5倍：',res[i]['xy'],)
        print('多单：',res[i]['duo'],'  ','空单：',res[i]['kong'],'  ','盈亏：',res[i]['mony'],'  ','详细：%s'%i,res[i]['datetimes'])
        zje+=res[i]['mony']
        print()
    print(zje)

if __name__=='__main__':
    ma=60 # 设置均线时长
    dates='2018-03-19' # 开始时间，这天必须有数据
    ts=5 # 要测试的天数
    main2(_ma=ma, _dates=dates, _ts=ts)

