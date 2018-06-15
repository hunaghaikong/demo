import datetime
import pandas as pd
from sklearn.externals import joblib
from collections import deque



class ZB(object):
    fa_doc = {
        '1': ["出现4次(收盘价小于60均线，价差除以标准差<-1.5）)则做多；若出现macd>0与收盘价大于60均线，则平仓。",
              "出现3次(收盘价大于60均线，价差除以标准差>1.5）)则做空；若出现macd<0与收盘价小于60均线，则平仓。","止损100个点"],
        '2': ["若出现前阳价差除以标准差>1.5与后阴价差除以标准差<-1.5重合，则做多；若出现前阴价差除以标准差<-1.5与后阳价差除以标准差>1.5倍重合，则平仓。",
              "若出现前阴价差除以标准差<-1.5与后阳价差除以标准差>1.5重合，则做空；若出现前阳价差除以标准差>1.5与后阴价差除以标准差<-1.5倍重合，则平仓。","止损100个点"],
        '3': ["收盘价小于60均线 与 价差除以标准差>1.5，则做多；若前阳价差除以标准差>1.5倍 与 后阴价差除以标准差<-1.5倍重合，则平仓。",
              "收盘价大于60均线 与 价差除以标准差<-1.5，则做空；若前阴价差除以标准差<-1.5倍 与 后阳价差除以标准差>1.5倍重合，则平仓。","止损100个点"],
        '4': ["收盘价大于60均线 与 价差除以标准差>1.5,则做多；若macd>0 与 收盘价小于60均线,则平仓；",
              "收盘价小于60均线 与 价差除以标准差<-1.5,则做空；若macd<0 与 收盘价大于60均线,则平仓；","止损100个点"],
        '5': ["价差除以标准差<-1,则做多；价差除以标准差> 1.5，则平仓。",
              "价差除以标准差> 1，则做空；价差除以标准差<-1.5,则平仓。","止损80个点"],
        "6": ["收盘价大于60均线 与 价差除以标准差>1.5，则做多；若前阳价差除以标准差>1.5倍 与 后阴价差除以标准差<-1.5倍重合，则平仓。",
              "收盘价小于60均线 与 价差除以标准差<-1.5，则做空；若前阴价差除以标准差<-1.5倍 与 后阳价差除以标准差>1.5倍重合，则平仓。","止损100个点"],
        "7":["收盘价小于60均线 与 价差除以标准差<-1.5，则做多；若macd<0 与 收盘价大于60均线，则平仓。",
             "收盘价大于60均线 与 价差除以标准差>1.5，则做空；若macd>0 与 收盘价小于60均线，则平仓。","止损100个点，全天止损200个点以上"],
        "8":["价差除以标准差<-1,并自行判断确定，则做多；价差除以标准差> 1.5，则平仓。",
              "价差除以标准差> 1，并自行判断确定，则做空；价差除以标准差<-1.5,则平仓。","止损80个点"],
        "9":["macd>0 与 当前macd所在区间的价格大于前面4波macd大于5的所在区间最高价的平均价格，则做多；macd<0 则平仓。",
             "macd<0 与 当前macd所在区间的价格小于前面4波macd小于-5的所在区间最低价的平均价格，则做空；macd>0 则平仓。","止损100个点"],
        "10":["收盘价小于60均线 与 价差除以标准差>1.5，在本macd区域（价差除以标准差>1.5）的次数小于3次，则做多；在第二波macd红绿区平仓",
              "","止损100个点。反测则为 收盘价大于60均线"],
        "11": ["",
               "收盘价小于60均线 与 价差除以标准差<-1.5，在本macd区域（价差除以标准差<-1.5）的次数小于3次，则做空；在第二波macd红绿区平仓", "止损100个点。反测则为 收盘价大于60均线"],
        "12": ["",
               "上一分钟的5分钟K值大于80，则做空；当前K值小于15 或者 KDJ（K）值已经突破了25 并且 当前K值比突破25的K值中的最小值大10，则平仓", "止损100个点。"],
        "13": ["上一分钟的5分钟K值小于20，则做多；当前K值大于80，则平仓。",
               "", "止损100个点。"],
        "14": ["收盘价大于60均线 与 dea大于0，则做多；收盘价小于60均线 与 dea小于0，则平仓。",
               "收盘价小于60均线 与 dea小于0，则做空；收盘价大于60均线 与 dea大于0，则平仓。", "止损100个点。"],
    }
    def __init__(self):
        #self.da = [(d[0], d[1], d[2], d[3], d[4]) for d in df.values]
        self.xzfa = {'1': self.fa1, '2': self.fa2, '3': self.fa3, '4': self.fa4,'5':self.fa5,'6':self.fa6,
                     '7':self.fa7,'9':self.fa9,'10':self.fa10,'11':self.fa11,'12':self.fa12,'13':self.fa13,
                     '14': self.fa14,}  # 执行方案 '8':self.fa8, '5':self.fa5,

    @property
    def zdata(self):
        return self._data

    @zdata.setter
    def zdata(self,ds):
        if isinstance(ds,pd.DataFrame):
            self._data = [(d[0], d[1], d[2], d[3], d[4]) for d in ds.values]
        elif isinstance(ds,list) or isinstance(ds,tuple):
            self._data = ds
        else:
            raise ValueError("zdata set ds,ds is not list or tuple or DataFrame! ")

    def get_doc(self,fa):
        return self.fa_doc.get(fa)

    def is_date(self,datetimes):
        ''' 是否已经或即将进入晚盘 '''
        h=datetimes.hour
        return (h==16 and datetimes.minute>=28) or h>16 or h<9

    def time_pd(self,dt1,dt2,fd=1):
        ''' 时间长度 '''
        dt1 = int(str(dt1)[11:16].replace(':',''))
        dt2 = int(dt2[11:16].replace(':',''))
        return dt1-dt2>fd

    def dt_kc(self,datetimes):
        ''' 开仓时间 '''
        h = datetimes.hour
        return (16 > h >= 9) or (h == 16 and datetimes.minute < 8)

    def sendNone(self,s):
        try:
            s.send(None)
        except:
            pass

    def vis(self,da,ma=60,short=12,long=26,phyd=9,k_min=5):
        ''' 各种指标初始化计算，动态计算 '''
        # da格式：((datetime.datetime(2018, 3, 19, 9, 22),31329.0,31343.0,31328.0,31331.0,249)...)
        dc=deque()
        co=0
        cds=1
        k_5 = 1 # 5 分钟数据以计算 K指标
        def body_k(o, h, l, c):
            if abs(h - l) > 0:
                return abs(o - c) / abs(h - l) > 0.6
            else:
                return False

        for i in range(len(da)):
            dc.append({'ema_short':0,'ema_long':0,'diff':0,'dea':0,'macd':0,'ma':0,'var':0,'std':0,'reg':0,'mul':0,'datetimes':da[i][0],'open':da[i][1],'high':da[i][2],'low':da[i][3],'close':da[i][4],'cd':0,'maidian':0,'rsi':0,
                       'open5':da[i][1],'high5':da[i][2],'low5':da[i][3],'close5':da[i][4],'k':50})
            if i == 1:
                ac = da[i - 1][4]
                this_c = da[i][4]
                dc[i]['ema_short'] = ac + (this_c - ac) * 2 / short
                dc[i]['ema_long'] = ac + (this_c - ac) * 2 / long
                #dc[i]['ema_short'] = sum([(short-j)*da[i-j][4] for j in range(short)])/(3*short)
                #dc[i]['ema_long'] = sum([(long-j)*da[i-j][4] for j in range(long)])/(3*long)
                dc[i]['diff'] = dc[i]['ema_short'] - dc[i]['ema_long']
                dc[i]['dea'] = dc[i]['diff'] * 2 / phyd
                dc[i]['macd'] = 2 * (dc[i]['diff'] - dc[i]['dea'])
                co=1 if dc[i]['macd']>=0 else 0
            elif i > 1:
                n_c = da[i][4]
                dc[i]['ema_short'] = dc[i-1]['ema_short'] * (short-2) / short + n_c * 2 / short
                dc[i]['ema_long'] = dc[i-1]['ema_long'] * (long-2) / long + n_c * 2 / long
                dc[i]['diff'] = dc[i]['ema_short'] - dc[i]['ema_long']
                dc[i]['dea'] = dc[i-1]['dea'] * (phyd-2) / phyd + dc[i]['diff'] * 2 / phyd
                dc[i]['macd'] = 2 * (dc[i]['diff'] - dc[i]['dea'])

                # 计算RSI
                # len_dc=len(dc)
                # rsia=0
                # rsib=0
                # for rsi in range(len_dc-14,len_dc):
                #     A=dc[rsi]['close']-dc[rsi]['open']
                #     if A>0:
                #         rsia+=A
                #     else:
                #         rsib+=(-A)
                # dc[i]['rsi'] = rsia/(rsia+rsib)*100

            if k_5%k_min == 0:
                dc[i]['open5'] = dc[i-k_min+1]['open5']
                dc[i]['high5'] = max(dc[i - j]['high5'] for j in range(k_min))
                dc[i]['low5'] = min(dc[i - j]['low5'] for j in range(k_min))
            k_5 += 1

            if i>=ma-1:
                dc[i]['ma']=sum(da[i-j][4] for j in range(ma))/ma # 移动平均值 i-ma+1,i+1
                std_pj=sum(da[i-j][4]-da[i-j][1] for j in range(ma))/ma
                dc[i]['var']=sum((da[i-j][4]-da[i-j][1]-std_pj)**2 for j in range(ma))/ma  # 方差 i-ma+1,i+1
                dc[i]['std']=float(dc[i]['var']**0.5) # 标准差

                if dc[i]['macd']>=0 and dc[i-1]['macd']<0:
                    co+=1
                elif dc[i]['macd']<0 and dc[i-1]['macd']>=0:
                    co+=1
                dc[i]['reg']=co
                price=dc[i]['close']-dc[i]['open']
                std=dc[i]['std']
                if std:
                    dc[i]['mul']=round(price/std,2)

                o1 = dc[i]['open']
                h1 = dc[i]['high']
                l1 = dc[i]['low']
                c1 = dc[i]['close']
                if abs(dc[i]['mul']) > 1.5 and body_k(o1, h1, l1, c1):
                    for j in range(i - 2, i - 15, -1):
                        o2 = dc[j]['open']
                        h2 = dc[j]['high']
                        l2 = dc[j]['low']
                        c2 = dc[j]['close']
                        oc = [o1,o2,c1,c2]
                        oc.sort()
                        try:
                            if not (max([o1, c1]) > min([o2, c2]) and min([o1, c1]) < max([o2, c2])):
                                continue
                            if abs(dc[j]['mul']) > 1.5 and ((o1 > c1 and o2 > c2) or (o1 < c1 and o2 < c2)) and body_k(o2, h2, l2, c2):
                                if o1 < c1:
                                    if dc[j]['cd'] == 0 and (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4 and o2 < o1 < c2 < c1:
                                        dc[i]['cd'] = cds
                                        cds += 1
                                        break
                                elif o1 > c1:
                                    if dc[j]['cd'] == 0 and (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4 and c1 < c2 < o1 < o2:
                                        dc[i]['cd'] = -cds
                                        cds += 1
                                        break

                            elif abs(dc[j]['mul']) > 1.5 and (o1 > c1 and o2 < c2 and (h1 <= h2 and l1 <= l2 or c1 <= o2)) and body_k(o2, h2, l2,c2):
                                if (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4:
                                    dc[i]['maidian'] = -cds
                                    break

                            elif abs(dc[j]['mul']) > 1.5 and (o1 < c1 and o2 > c2) and (h1 >= h2 and l1 >= l2 or c1 >= o2) and body_k(o2, h2, l2,c2):
                                if (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4:
                                    dc[i]['maidian'] = cds
                                    break
                        except:
                            continue

        data=1 # data future is list
        while data:
            data=yield dc
            dc.popleft()
            ind=59 # len(dc)
            if isinstance(data,tuple) or isinstance(data,list):
                dc.append({'ema_short':0,'ema_long':0,'diff':0,'dea':0,'macd':0,'ma':0,'var':0,'std':0,'reg':0,'mul':0,'datetimes':data[0],'open':data[1],'high':data[2],'low':data[3],'close':data[4],'cd':0,'maidian':0})
                try:
                    dc[ind]['ema_short'] = dc[ind-1]['ema_short'] * (short-2) / short + dc[ind]['close'] * 2 / short  # 当日EMA(12)
                    dc[ind]['ema_long'] = dc[ind-1]['ema_long'] * (long-2) / long + dc[ind]['close'] * 2 / long  # 当日EMA(26)
                    dc[ind]['diff'] = dc[ind]['ema_short'] - dc[ind]['ema_long']
                    dc[ind]['dea'] = dc[ind-1]['dea'] * (phyd-2) / phyd + dc[ind]['diff'] * 2 / phyd
                    dc[ind]['macd'] = 2 * (dc[ind]['diff'] - dc[ind]['dea'])

                    dc[ind]['ma']=sum(dc[ind-j]['close'] for j in range(ma))/ma # 移动平均值
                    std_pj=sum(dc[ind-j]['close']-dc[ind-j]['open']  for j in range(ma))/ma
                    dc[ind]['var']=sum((dc[ind-j]['close']-dc[ind-j]['open']-std_pj)**2 for j in range(ma))/ma # 方差
                    dc[ind]['std']=float(dc[ind]['var']**0.5) # 标准差
                    # 计算K 指标
                    # 计算K 指标
                    # n日RSV =（Cn－Ln） / （Hn－Ln）×100
                    # 公式中，Cn为第n日收盘价；Ln为n日内的最低价；Hn为n日内的最高价。
                    # 其次，计算K值与D值：
                    # 当日K值 = 2 / 3×前一日K值 + 1 / 3×当日RSV
                    # 当日D值 = 2 / 3×前一日D值 + 1 / 3×当日K值
                    # 若无前一日K
                    # 值与D值，则可分别用50来代替。
                    if k_5%k_min == 0:
                        Ln = min(dc[ind - j]['low'] for j in range(0,k_min*9,k_min))
                        Hn = max(dc[ind - j]['high'] for j in range(0,k_min*9,k_min))
                        rsv = (data[4] - Ln) / (Hn - Ln) * 100
                        dc[ind]['k'] = dc[ind - 1]['k'] * 2 / 3 + rsv / 3
                    else:
                        dc[ind]['k'] = dc[ind-1]['k']
                    k_5 += 1
                    # Cn = da[i][4]
                    # Ln = min(da[i - j][3] for j in range(9))
                    # Hn = max(da[i - j][2] for j in range(9))
                    # rsv = (Cn - Ln) / (Hn - Ln) * 100
                    # dc[i]['k'] = dc[i - 1]['k'] * 2 / 3 + rsv / 3
                    # 计算RSI
                    # len_dc = len(dc)
                    # rsia = 0
                    # rsib = 0
                    # for rsi in range(len_dc - 14, len_dc):
                    #     A = dc[rsi]['close'] - dc[rsi]['open']
                    #     if A > 0:
                    #         rsia += A
                    #     else:
                    #         rsib += (-A)
                    # dc[i]['rsi'] = rsia / (rsia + rsib) * 100
                except Exception as exc:
                    print(exc)

                if dc[ind]['macd']>=0 and dc[ind-1]['macd']<0:
                    co+=1
                elif dc[ind]['macd']<0 and dc[ind-1]['macd']>=0:
                    co+=1
                dc[ind]['reg']=co
                price=dc[ind]['close']-dc[ind]['open']
                std=dc[ind]['std']
                if std:
                    dc[ind]['mul']=round(price/std,2)

                o1 = dc[ind]['open']
                h1 = dc[ind]['high']
                l1 = dc[ind]['low']
                c1 = dc[ind]['close']
                if abs(dc[ind]['mul']) > 1.5 and body_k(o1, h1, l1, c1):
                    for j in range(ind - 1, ind - 12, -1):
                        o2 = dc[j]['open']
                        h2 = dc[j]['high']
                        l2 = dc[j]['low']
                        c2 = dc[j]['close']
                        try:
                            if not (max([o1, c1]) > min([o2, c2]) and min([o1, c1]) < max([o2, c2])):
                                continue
                            oc = [o1, o2, c1, c2]
                            oc.sort()
                            mul_15 = abs(dc[j]['mul'])
                            if mul_15 > 1.5 and ((o1 > c1 and o2 > c2) or (o1 < c1 and o2 < c2)) and body_k(
                                    o2, h2, l2, c2):
                                if o1 < c1:
                                    if dc[j]['cd'] == 0 and (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4:
                                        dc[ind]['cd'] = cds
                                        cds += 1
                                        break
                                elif o1 > c1:
                                    if dc[j]['cd'] == 0 and (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4:
                                        dc[ind]['cd'] = -cds
                                        cds += 1
                                        break
                            elif mul_15 > 1.5 and (o1 > c1 and o2 < c2 and (h1 <= h2 and l1 <= l2 or c1 <= o2)):  # and body_k(o2, h2, l2,c2):
                                if (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4:
                                    dc[ind]['maidian'] = -cds
                                    break

                            elif mul_15 > 1.5 and (o1 < c1 and o2 > c2) and (h1 >= h2 and l1 >= l2 or c1 >= o2):  # and body_k(o2, h2, l2,c2):
                                if (oc[2] - oc[1]) / (oc[3] - oc[0]) > 0.4:
                                    dc[ind]['maidian'] = cds
                                    break
                        except Exception as exc:
                            continue
            else:
                print('data不是tuple',type(data),data)

    def dynamic_index(self,data,_ma=60,zsjg=-100):
        ''' 动态交易指标 '''
        res={}
        is_d=0
        is_k=0
        #conn=get_conn('carry_investment')
        #sql='SELECT a.datetime,a.open,a.high,a.low,a.close FROM futures_min a INNER JOIN (SELECT DATETIME FROM futures_min ORDER BY DATETIME DESC LIMIT 0,{})b ON a.datetime=b.datetime'.format(_ma)
        #data=getSqlData(conn,sql)
        data2=self.vis(da=data,ma=_ma)
        dt2=data2.send(None)
        data=1
        while data:
            data=yield res
            dates=data[0]
            res[dates]={'duo':0,'kong':0,'mony':0,'datetimes':[],'dy':0,'xy':0}
            #str_time1=None if is_d==0 else str_time1
            #str_time2=None if is_k==0 else str_time2
            jg_d=0 if is_d==0 else jg_d
            jg_k=0 if is_k==0 else jg_k
            is_dk = not (is_k or is_d)
            # data格式：(datetime.datetime(2018, 3, 26, 20, 19), 30606.0, 30610.0, 30592.0, 30597.0)
            dt2=data2.send(data)[-1:][0]

            datetimes,clo,macd,mas,std,reg,mul=dt2['datetimes'],dt2['close'],dt2['macd'],dt2['ma'],dt2['std'],dt2['reg'],dt2['mul']
            # if mul>1.5:
            #     res[dates]['dy']+=1
            # if mul<-1.5:
            #     res[dates]['xy']+=1
            if clo < mas and mul < -1.5 and is_dk and self.dt_kc(datetimes):
                jg_d=clo
                str_time1 = str(datetimes)
                res[dates]['datetimes'].append([str_time1,1])
                is_d=1
            elif clo > mas and mul > 1.5 and is_dk and self.dt_kc(datetimes):
                jg_k=clo
                str_time2 = str(datetimes)
                res[dates]['datetimes'].append([str_time2,-1])
                is_k=-1
            if is_d==1 and ((macd<0 and clo>mas) or clo-jg_d<zsjg or self.is_date(datetimes)):
                if self.time_pd(str(datetimes),str_time1,3):
                    res[dates]['duo']+=1
                    res[dates]['mony']+=(clo-jg_d)
                    res[dates]['datetimes'].append([str(datetimes),2])
                    is_d=0
            elif is_k == -1 and ((macd > 0 and clo < mas) or jg_k - clo < zsjg or self.is_date(datetimes)):
                if self.time_pd(str(datetimes), str_time2, 3):
                    res[dates]['kong']+=1
                    res[dates]['mony']+=(jg_k-clo)
                    res[dates]['datetimes'].append([str(datetimes),-2])
                    is_k=0
        self.sendNone(data2)

    def fa1(self, zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2=zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        tj_d=0
        tj_k=0
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            # while循环判断，数据重用，一行原始数据，日期，是否强制平仓
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high,low = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = clo<mas and mul<-1.5
            kctj_k = clo>mas and mul>1.5
            pctj_d = (macd>0 and clo>mas)
            pctj_k = (macd<0 and clo<mas)

            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and 9<=datetimes.hour<16:
                tj_d+=1
                if tj_d>3:
                    jg_d=clo
                    startMony_d=clo
                    str_time1=str(datetimes)
                    is_d=1
                    first_time = [str_time1,'多' ,clo]
                    zsjg = low-clo-1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and 9<=datetimes.hour<16:
                tj_k+=1
                if tj_k>2:
                    jg_k=clo
                    startMony_k=clo
                    str_time2=str(datetimes)
                    is_k=-1
                    first_time = [str_time2, '空' ,clo]
                    zsjg = clo-high-1 if zsjg2 >= -10 else zsjg

            if is_d==1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((pctj_d or self.is_date(datetimes) or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes)!=str_time1:
                    res[dates]['duo'] += 1
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo-startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d,2)
                        zszy = -1  # 止损
                    elif high-startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    #price = round(_zsjg_d - startMony_d if low<=_zsjg_d else (zyds if high-startMony_d>=zyds else clo-startMony_d))

                    price -= cqdc
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price, zszy])
                    is_d = 0
                    first_time = []
                    tj_d=0
                    _zsjg_d = 0
                    ydzs_d = 0
                    # elif clo - jg_d > 60:
                    #     res[dates]['mony'] += (clo - jg_d)
                    #     jg_d = clo
            elif is_k==-1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k==0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if ((pctj_k or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes)!=str_time2:
                    res[dates]['kong'] += 1
                    if high < _zsjg_k and startMony_k-low < zyds:
                        price = round(startMony_k-clo)
                        zszy = 0  # 正常平仓
                    elif high>=_zsjg_k:
                        price = round(startMony_k - _zsjg_k,2)
                        zszy = -1  # 止损
                    elif startMony_k-low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    #price = round(startMony_k - _zsjg_k if high>=_zsjg_k else (zyds if startMony_k-low>=zyds else startMony_k-clo))
                    price -= cqdc
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price, zszy])
                    is_k = 0
                    first_time = []
                    tj_k=0
                    _zsjg_k = 0
                    ydzs_k = 0
                    # elif jg_k - clo > 60:
                    #     res[dates]['mony'] += (jg_k - clo)
                    #     jg_k = clo

    def fa2(self, zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low, maidian = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low'], dt2['maidian']

            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = maidian < 0
            kctj_k = maidian > 0
            pctj_d = maidian > 0
            pctj_k = maidian < 0
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and self.dt_kc(datetimes):
                res[dates]['duo'] += 1
                startMony_d=clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str_time1, '多' ,clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and self.dt_kc(datetimes):
                res[dates]['kong'] += 1
                startMony_k=clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg
            if is_d == 1:
                ydzs_d = high if (ydzs_d==0 or high>ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点

                if ((pctj_d or self.is_date(datetimes) or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes)!=str_time1:
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price, zszy])
                    is_d = 0
                    first_time = []
                    _zsjg_d = 0
                    ydzs_d = 0
            elif is_k == -1:
                ydzs_k = low if (ydzs_k==0 or ydzs_k>low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点

                if ((pctj_k or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes)!=str_time2:
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price, zszy])
                    is_k = 0
                    first_time = []
                    _zsjg_k = 0
                    ydzs_k = 0

    def fa3(self, zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low, maidian = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'],dt2['high'], dt2['low'], dt2['maidian']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = clo<mas and mul>1.5
            kctj_k = clo>mas and mul<-1.5
            pctj_d = maidian<0
            pctj_k = maidian>0
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and self.dt_kc(datetimes):
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1, '多' ,clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and self.dt_kc(datetimes):
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_d==1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点

                if (self.time_pd(datetimes,str_time1,2) and (pctj_d or self.is_date(datetimes)) or low<=_zsjg_d or high-startMony_d>=zyds or qzpc) and str(datetimes)!=str_time1:
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['duo'] += 1
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes),'多',price, zszy])
                    is_d=0
                    first_time = []
                    ydzs_d = 0

            elif is_k==-1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点

                if (self.time_pd(datetimes,str_time2,2) and (pctj_k or self.is_date(datetimes)) or high>=_zsjg_k or startMony_k-low>=zyds or qzpc) and str(datetimes)!=str_time2:
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['kong']+=1
                    res[dates]['mony']+=price
                    res[dates]['datetimes'].append([str_time2,str(datetimes),'空',price, zszy])
                    is_k=0
                    first_time = []
                    ydzs_k = 0

    def fa4(self, zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = clo>mas and mul>1.5
            kctj_k = clo<mas and mul<-1.5
            pctj_d = macd>0 and clo<mas
            pctj_k = macd<0 and clo>mas
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and self.dt_kc(datetimes):
                res[dates]['duo'] += 1
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1, '多' ,clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and self.dt_kc(datetimes):
                res[dates]['kong'] += 1
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg
            if is_d==1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((pctj_d or self.is_date(datetimes)) and self.time_pd(str(datetimes),str_time1,3) or low<=_zsjg_d or high-startMony_d>=zyds or qzpc) and str(datetimes)!=str_time1:
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['mony']+=price
                    res[dates]['datetimes'].append([str_time1,str(datetimes),'多',price,zszy])
                    is_d=0
                    first_time = []
                    ydzs_d = 0
            elif is_k==-1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if ((pctj_k or self.is_date(datetimes)) and self.time_pd(str(datetimes), str_time2, 3) or high>=_zsjg_k or startMony_k-low>=zyds or qzpc) and str(datetimes)!=str_time2:
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈

                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['mony']+=price
                    res[dates]['datetimes'].append([str_time2,str(datetimes),'空',price,zszy])
                    is_k=0
                    first_time = []
                    ydzs_k = 0

    def fa5(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        up_c, down_c = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, maidian, high, low = dt2['datetimes'], dt2['open'], dt2[
                'close'], dt2[
                                                                                        'macd'], dt2['ma'], dt2['std'], \
                                                                                    dt2['reg'], dt2['mul'], dt2['cd'], \
                                                                                    dt2['maidian'], dt2['high'], dt2[
                                                                                        'low']

            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = mul < -1
            kctj_k = mul > 1
            pctj_d = mul > 1.5
            pctj_k = mul < -1.5
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and self.dt_kc(datetimes):  # is_d!=1 and judge_d
                jg_d = clo
                startMony_d = clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str(datetimes), '多' ,clo]

            elif kctj_k and self.dt_kc(datetimes):  # is_k!=-1 and judge_k
                jg_k = clo
                startMony_k = clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str(datetimes), '空' ,clo]

            if (is_d == 1 and (pctj_d or self.is_date(datetimes) or low - startMony_d - cqdc < zsjg) or qzpc) and str(datetimes)!=str_time1:
                res[dates]['duo'] += 1
                price=zsjg if low - startMony_d - cqdc < zsjg else clo - startMony_d - cqdc
                res[dates]['mony'] += price
                res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price])
                is_d = 0
                first_time = []

            elif (is_k == -1 and (pctj_k or self.is_date(datetimes) or startMony_k - high - cqdc < zsjg) or qzpc) and str(datetimes)!=str_time2:
                res[dates]['kong'] += 1
                price=zsjg if startMony_k - high - cqdc < zsjg else startMony_k - clo - cqdc
                res[dates]['mony'] += price
                res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price])
                is_k = 0
                first_time = []

    def fa6(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd ,high, low,maidian= dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low'], dt2['maidian']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = clo>mas and mul>1.5
            kctj_k = clo<mas and mul<-1.5
            pctj_d = maidian<0
            pctj_k = maidian>0
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and 9<datetimes.hour<16:
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1,'多' ,clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and 9<datetimes.hour<16:
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_d==1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((self.is_date(datetimes) or pctj_d or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes)!=str_time1:
                    res[dates]['duo'] += 1
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price,zszy])
                    is_d = 0
                    first_time = []
                    ydzs_d = 0

            elif is_k==-1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if ((self.is_date(datetimes) or pctj_k or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes)!=str_time2:
                    res[dates]['kong'] += 1
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price,zszy])
                    is_k = 0
                    first_time = []
                    ydzs_k = 0

    def fa7(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        while 1:
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low  = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            h = datetimes.hour
            this_date = (h == 23 and datetimes.minute >= 56) or h < 9

            # 反向做单
            kctj_d = clo<mas and mul<-1.5
            kctj_k = clo>mas and mul>1.5
            pctj_d = (macd<0 and clo>mas)
            pctj_k = (macd>0 and clo<mas)
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and not this_date and not res[dates]['mony']<-200:
                res[dates]['duo'] += 1
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1, '多' ,clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and not this_date and not res[dates]['mony']<-200:
                res[dates]['kong'] += 1
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_d==1 and (pctj_d or low-startMony_d-cqdc<zsjg or this_date) or qzpc:
                price=zsjg if low-startMony_d-cqdc<zsjg else clo - startMony_d - cqdc
                if this_date or qzpc:
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price])
                    is_d = 0
                    first_time = []
                elif self.time_pd(str(datetimes),str_time1,3):
                    res[dates]['mony']+=price
                    res[dates]['datetimes'].append([str_time1,str(datetimes),'多',price])
                    is_d=0
                    first_time = []
                elif str_time1[:10]!=str(datetimes)[:10]:
                    #res[dates]['mony'] += (clo - jg_d - cqdc)
                    #res[dates]['datetimes'].append([str_time1, str(datetimes), '多', clo - startMony_d - cqdc])
                    is_d = 0
                    first_time = []

            elif is_k==-1 and (pctj_k or startMony_k-high-cqdc<zsjg or this_date) or qzpc:
                price=zsjg if startMony_k-high-cqdc<zsjg else startMony_k - clo - cqdc
                if this_date or qzpc:
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price])
                    is_k = 0
                    first_time = []
                elif self.time_pd(str(datetimes), str_time2, 3):
                    res[dates]['mony']+=price
                    res[dates]['datetimes'].append([str_time2,str(datetimes),'空',price])
                    is_k=0
                    first_time = []
                elif str_time1[:10]!=str(datetimes)[:10]:
                    #res[dates]['mony'] += (jg_k - clo - cqdc)
                    #res[dates]['datetimes'].append([str_time2, str(datetimes), '空', startMony_k - clo - cqdc])
                    is_k = 0
                    first_time = []

    def fa8(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        up_c,down_c=0,0
        startMony_d,startMony_k=0,0
        str_time1,str_time2='',''
        is_d,is_k=0,0
        res={}
        first_time=[]
        svmDK=joblib.load("log\\svms2.m")
        _high=None
        _low=None
        svm=0
        while 1:
            _while, res, dt3, dates = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd ,maidian,high,low= dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['maidian'],dt2['high'],dt2['low']
            #zsjg=-(3*std)
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0
            #up_c += 1 if mul>1.5 else 0 # 上涨提示次数
            #down_c += 1 if mul<-1.5 else 0 # 下跌提示次数

            #judge_d=(up_c>down_c and up_c>1) # 做多与平多仓的判断
            #judge_k=(down_c>up_c and down_c>1) # 做空与平空仓的判断
            #print(is_dk and svmDK.predict([[ope,high,low,clo]])[0]==-1)

            svm=svmDK.predict([[ope, high, low, clo]])
            svm = True if svm[0]>0 else False

            if mul<-1 and svm and is_dk and self.dt_kc(datetimes): # is_dk and judge_d svmDK.predict([[ope,high,low,clo]])[0]==1
                jg_d = clo
                startMony_d=clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str(datetimes), '多' ,clo]
                _high = high
                #test_d.append([ope,high,low,clo])

            elif mul>1 and not svm and is_dk and self.dt_kc(datetimes): # is_dk and judge_k svmDK.predict([[ope,high,low,clo]])[0]==-1
                jg_k = clo
                startMony_k=clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str(datetimes), '空' ,clo]
                _low = low
                #test_k.append([ope,high,low,clo])

            if is_d == 1 and (mul>1.5 or self.is_date(datetimes) or low - startMony_d-cqdc<zsjg):
                res[dates]['duo'] += 1
                price=zsjg if low - startMony_d-cqdc<zsjg else clo - startMony_d-cqdc
                res[dates]['mony'] += price
                res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price])
                is_d = 0
                up_c = 0
                down_c = 0
                first_time = []


            elif is_k == -1 and (mul<-1.5 or self.is_date(datetimes) or startMony_k - high-cqdc<zsjg):
                res[dates]['kong'] += 1
                price=zsjg if startMony_k - high-cqdc<zsjg else startMony_k - clo-cqdc
                res[dates]['mony'] += price
                res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price])
                is_k = 0
                up_c = 0
                down_c = 0
                first_time = []

    def fa9(self, zsjg=-100, ydzs=80, zyds=300, cqdc=6, reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        sb = []
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)

            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low = dt2['datetimes'], dt2['open'], dt2['close'], \
                                                                           dt2[
                                                                               'macd'], dt2['ma'], dt2['std'], dt2[
                                                                               'reg'], dt2['mul'], dt2['cd'], dt2[
                                                                               'high'], dt2['low']
            if ((sb and sb[-1][0] != reg) or not sb):
                sb.append([reg, macd, clo])
            elif sb[-1][0] == reg and macd < 0:
                sb[-1][1] = macd if sb[-1][1] > macd else sb[-1][1]
                sb[-1][2] = clo if sb[-1][2] > clo else sb[-1][2]
            elif sb[-1][0] == reg and macd > 0:
                sb[-1][1] = macd if sb[-1][1] < macd else sb[-1][1]
                sb[-1][2] = clo if sb[-1][2] < clo else sb[-1][2]
            if len(sb) > 18:
                sb.pop(0)

            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            vv = sum(v[1] for v in sb[-3:-10:-2]) / len(sb[-3:-10:-2]) if len(sb[-3:-10:-2]) > 0 else 1
            kctj_d = macd > 0 and len(sb) > 2 and (sb[-1][1] > vv > 5)
            kctj_k = macd < 0 and len(sb) > 2 and (sb[-1][1] < vv < -5)
            pctj_d = macd < 0
            pctj_k = macd > 0
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and 9 <= datetimes.hour < 16:
                startMony_d = clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str_time1, '多', clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg

            elif kctj_k and is_dk and 9 <= datetimes.hour < 16:
                startMony_k = clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str_time2, '空', clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_d == 1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((pctj_d or self.is_date(
                        datetimes) or low <= _zsjg_d or high - startMony_d >= zyds) or qzpc) and str(
                        datetimes) != str_time1:
                    res[dates]['duo'] += 1
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price, zszy])
                    is_d = 0
                    first_time = []
                    ydzs_d = 0

            elif is_k == -1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if ((pctj_k or self.is_date(
                        datetimes) or high >= _zsjg_k or startMony_k - low >= zyds) or qzpc) and str(
                        datetimes) != str_time2:
                    res[dates]['kong'] += 1
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price, zszy])
                    is_k = 0
                    first_time = []
                    ydzs_k = 0

    def fa10(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        sb = 0
        sb2 = 0
        count = 0
        count_c = 0
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low = dt2['datetimes'], dt2['open'], dt2['close'], \
                                                                           dt2[
                                                                               'macd'], dt2['ma'], dt2['std'], dt2[
                                                                               'reg'], dt2['mul'], dt2['cd'], dt2[
                                                                               'high'], dt2['low']

            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            kctj_d = clo < mas
            kctj_k = clo > mas
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d

            if not is_dk and sb == reg and mul > 1.5:
                count_c += 1

            if kctj_d and count_c<3 and mul > 1.5 and is_dk and 9 <= datetimes.hour < 16:
                startMony_d = clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str_time1, '多', clo]
                sb = reg
                sb2 = reg%2
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            # elif kctj_k and mul < -1.5 and is_dk and 9 <= datetimes.hour < 16:
            #     startMony_k = clo
            #     str_time2 = str(datetimes)
            #     is_k = -1
            #     first_time = [str_time2, '空', clo]
            #     sb = reg

            if not is_dk and sb != reg and abs(macd)>5:
                count += 1
                sb = reg

            if is_d == 1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if (((count > 2 and sb2 != reg%2) or self.is_date(datetimes) or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes)!=str_time1:
                    res[dates]['duo'] += 1
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price,zszy])
                    is_d = 0
                    first_time = []
                    count = 0
                    count_c = 0
                    ydzs_d = 0
            # elif is_k == -1 and (count > 2 or self.is_date(datetimes) or startMony_k - high - cqdc < zsjg):
            #     res[dates]['kong'] += 1
            #     price = zsjg if startMony_k - high - cqdc < zsjg else startMony_k - clo - cqdc
            #     res[dates]['mony'] += price
            #     res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price])
            #     is_k = 0
            #     first_time = []
            #     count = 0

    def fa11(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        sb = 0
        sb2 = 0
        count = 0
        count_c = 0
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        vs = 0
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low = dt2['datetimes'], dt2['open'], dt2['close'], \
                                                                           dt2[
                                                                               'macd'], dt2['ma'], dt2['std'], dt2[
                                                                               'reg'], dt2['mul'], dt2['cd'], dt2[
                                                                               'high'], dt2['low']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            kctj_k = clo < mas
            kctj_d = clo > mas
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d

            # if kctj_d and mul > 1.5 and is_dk and 9 <= datetimes.hour < 16:
            #     startMony_d = clo
            #     str_time1 = str(datetimes)
            #     is_d = 1
            #     first_time = [str_time1, '多', clo]
            #     sb = reg
            if not is_dk and sb == reg and mul < -1.5:
                count_c += 1
            if kctj_k and count_c<3 and mul < -1.5 and is_dk and 9 <= datetimes.hour < 16:
                startMony_k = clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str_time2, '空', clo]
                sb = reg
                sb2 = reg%2
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg
                count = 0

            if sb != reg:
                if abs(macd)>5:
                    count += 1
                    sb = reg


            # if is_d == 1 and (count > 2 or self.is_date(datetimes) or low - startMony_d - cqdc < zsjg):
            #     res[dates]['duo'] += 1
            #     price = zsjg if low - startMony_d - cqdc < zsjg else clo - startMony_d - cqdc
            #     res[dates]['mony'] += price
            #     res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price])
            #     is_d = 0
            #     first_time = []
            #     count = 0
            if is_k == -1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if (((count > 2 and sb2!=reg%2) or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes)!=str_time2:
                    res[dates]['kong'] += 1
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈

                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price,zszy])
                    is_k = 0
                    first_time = []
                    count = 0
                    count_c = 0
                    ydzs_k = 0

    def fa12(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        k5s = []
        k58s = []
        ydzs_k = 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low, k5 = dt2['datetimes'], dt2['open'], dt2['close'], \
                                                                           dt2[
                                                                               'macd'], dt2['ma'], dt2['std'], dt2[
                                                                               'reg'], dt2['mul'], dt2['cd'], dt2[
                                                                               'high'], dt2['low'], dt2['k']

            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            kctj_k = dt3[-2]['k']>85 #and dt3[-2]['k']-k5>5 # clo < mas
            kctj_d = dt3[-2]['k']<10
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d


            # if kctj_d and is_dk and self.dt_kc(datetimes):
            #     startMony_d = clo
            #     str_time1 = str(datetimes)
            #     is_d = 1
            #     first_time = [str_time1, '多', clo]
            #     sb = reg
            #     zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            if kctj_k and is_dk and self.dt_kc(datetimes): # and mul < -1.5
                startMony_k = clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str_time2, '空', clo]
                sb = reg
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_k == -1 and k5<25:
                k5s.append(k5)
            if is_k == -1 and k5<80:
                k58s.append(k5)

            a={"12":["",
                  "上一分钟的5分钟K值大于80，则做空；当前K值小于15 或者 K值已经突破了25 并且 当前K值比突破25的K值中的最小值大10", "止损100个点。反测则为 收盘价大于60均线"],}
            if is_k == -1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.4  # 止损所在价格点，至少盈利20%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if (((k5<15 or k5s and k5-min(k5s)>10 or len(k58s)>=1 and k5>80) or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) and str(datetimes)!=str_time2) or qzpc:
                    res[dates]['kong'] += 1
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈

                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price,zszy])
                    is_k = 0
                    first_time = []
                    k5s = []
                    k58s = []
                    ydzs_k = 0

    def fa13(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        k5s = []
        ydzs_d = 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low, k5 = dt2['datetimes'], dt2['open'], dt2['close'], \
                                                                           dt2[
                                                                               'macd'], dt2['ma'], dt2['std'], dt2[
                                                                               'reg'], dt2['mul'], dt2['cd'], dt2[
                                                                               'high'], dt2['low'], dt2['k']

            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            kctj_k = dt3[-2]['k']<20 #and dt3[-2]['k']-k5>5 # clo < mas
            kctj_d = dt3[-2]['k']>80
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d


            if kctj_k and is_dk and self.dt_kc(datetimes):
                startMony_d = clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str_time1, '多', clo]
                sb = reg
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg
            # if kctj_k and is_dk and self.dt_kc(datetimes): # and mul < -1.5
            #     startMony_k = clo
            #     str_time2 = str(datetimes)
            #     is_k = -1
            #     first_time = [str_time2, '空', clo]
            #     zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_d == 1 and k5>50:
                k5s.append(k5)

            if is_d == 1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((k5>80 or self.is_date(datetimes) or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes)!=str_time1:
                    res[dates]['duo'] += 1
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price,zszy])
                    is_d = 0
                    first_time = []
                    k5s = []
                    ydzs_d = 0
            # if is_k == -1:
            #     low_zs = startMony_k - low
            #     if low_zs >= ydzs:
            #         _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
            #     elif _zsjg_k == 0:
            #         _zsjg_k = startMony_k - zsjg  # 止损所在价格点
            #     if ((( k5<20) or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes)!=str_time2:
            #         res[dates]['kong'] += 1
            #         price = round(startMony_k - _zsjg_k if high >= _zsjg_k else (
            #             zyds if startMony_k - low >= zyds else startMony_k - clo))
            #         price -= cqdc
            #         _zsjg_k = 0
            #         res[dates]['mony'] += price
            #         res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price])
            #         is_k = 0
            #         first_time = []
            #         k5s = []

    def fa14(self,zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False):
        zsjg2 = zsjg
        _zsjg_d, _zsjg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        breach = deque()
        count = 0
        first_time = []
        ydzs_d, ydzs_k = 0, 0  # 移动止损
        while 1:
            _while, res, dt3, dates, qzpc = yield res, first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)

            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high, low, dea = dt2['datetimes'], dt2['open'], dt2['close'], \
                                                                           dt2[
                                                                               'macd'], dt2['ma'], dt2['std'], dt2[
                                                                               'reg'], dt2['mul'], dt2['cd'], dt2[
                                                                               'high'], dt2['low'], dt2['dea']


            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            sb = 1 if clo > mas and dea > 0 else (-1 if clo < mas and dea < 0 else 0)


            kctj_d = (sb == 1 and sb != breach[-1]) if breach else False
            kctj_k = (sb == -1 and sb != breach[-1]) if breach else False
            pctj_d = kctj_k # count > 1 #
            pctj_k = kctj_d
            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if ((breach and breach[-1] != sb) or not breach):
                breach.append(sb)
            if len(breach)>18:
                breach.popleft()

            if kctj_d and is_d!=1 and 9 <= datetimes.hour < 16:
                startMony_d = clo
                str_time1 = str(datetimes)
                is_d = 1
                first_time = [str_time1, '多' ,clo]
                zsjg = low - clo - 1 if zsjg2 >= -10 else zsjg

            if kctj_k and is_k!=-1 and 9 <= datetimes.hour < 16:
                startMony_k = clo
                str_time2 = str(datetimes)
                is_k = -1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo - high - 1 if zsjg2 >= -10 else zsjg

            if is_d == 1:
                ydzs_d = high if (ydzs_d == 0 or high > ydzs_d) else ydzs_d
                high_zs = ydzs_d - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.3  # 止损所在价格点，至少盈利30%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((pctj_d or self.is_date(datetimes) or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes)!=str_time1:
                    res[dates]['duo'] += 1
                    if low > _zsjg_d and high - startMony_d < zyds:
                        price = round(clo - startMony_d)
                        zszy = 0  # 正常平仓
                    elif low <= _zsjg_d:
                        price = round(_zsjg_d - startMony_d, 2)
                        zszy = -1  # 止损
                    elif high - startMony_d >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_d = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price,zszy])
                    is_d = 0
                    first_time = []
                    ydzs_d = 0

            if is_k == -1:
                ydzs_k = low if (ydzs_k == 0 or ydzs_k > low) else ydzs_k
                low_zs = startMony_k - ydzs_k
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.3  # 止损所在价格点，至少盈利30%
                elif _zsjg_k == 0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if ((pctj_k or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes)!=str_time2:
                    res[dates]['kong'] += 1
                    if high < _zsjg_k and startMony_k - low < zyds:
                        price = round(startMony_k - clo)
                        zszy = 0  # 正常平仓
                    elif high >= _zsjg_k:
                        price = round(startMony_k - _zsjg_k, 2)
                        zszy = -1  # 止损
                    elif startMony_k - low >= zyds:
                        price = zyds
                        zszy = 1  # 止盈
                    price -= cqdc
                    _zsjg_k = 0
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price,zszy])
                    is_k = 0
                    first_time = []
                    ydzs_k = 0

    def fa_new(self, zsjg=-100, ydzs=100, zyds=200, cqdc=6,reverse=False, param=None):
        zsjg2=zsjg
        _zsjg_d, _zsjg_k = 0, 0
        jg_d, jg_k = 0, 0
        startMony_d, startMony_k = 0, 0
        str_time1, str_time2 = '', ''
        is_d, is_k = 0, 0
        res = {}
        first_time = []
        # duo_macd, duo_avg, duo_yidong, duo_chonghes, duo_chonghed, kong_macd, kong_avg, kong_yidong, kong_chonghes, kong_chonghed, pdd_macd, pdd_avg, pdd_yidong, pdd_chonghes, pdd_chonghed, pkd_macd, pkd_avg, pkd_yidong, pkd_chonghes, pkd_chonghed
        choices = lambda x,y,z: x if y == '0' else (z if y == '1' else True)
        while 1:
            # while循环判断，数据重用，一行原始数据，日期，是否强制平仓
            _while, res, dt3, dates, qzpc = yield res,first_time
            if not _while:
                break
            is_dk = not (is_k or is_d)
            dt2 = dt3[-1]
            datetimes, ope, clo, macd, mas, std, reg, mul, cd, high,low, maidian = dt2['datetimes'], dt2['open'], dt2['close'], dt2[
                'macd'], dt2['ma'], dt2['std'], dt2['reg'], dt2['mul'], dt2['cd'], dt2['high'], dt2['low'], dt2['maidian']
            if mul > 1.5:
                res[dates]['dy'] += 1
            elif mul < -1.5:
                res[dates]['xy'] += 1
            res[dates]['ch'] += 1 if cd != 0 else 0

            # 反向做单
            kctj_d = choices(macd<0, param['duo_macd'],macd>0)
            kctj_d = kctj_d and choices(clo<mas,param['duo_avg'],clo>mas)
            kctj_d = kctj_d and choices(mul<-1.5, param['duo_yidong'], mul>1.5)
            kctj_d = kctj_d and choices(cd < 0, param['duo_chonghes'], cd > 0)
            kctj_d = kctj_d and choices(maidian < 0, param['duo_chonghed'], maidian > 0)
            kctj_d = kctj_d if param['duo'] else False

            #kctj_k = clo>mas and mul>1.5
            kctj_k = choices(macd < 0, param['kong_macd'], macd > 0)
            kctj_k = kctj_k and choices(clo < mas, param['kong_avg'], clo > mas)
            kctj_k = kctj_k and choices(mul < -1.5, param['kong_yidong'], mul > 1.5)
            kctj_k = kctj_k and choices(cd < 0, param['kong_chonghes'], cd > 0)
            kctj_k = kctj_k and choices(maidian < 0, param['kong_chonghed'], maidian > 0)
            kctj_k = kctj_k if param['kong'] else False

            #pctj_d = (macd>0 and clo>mas)
            pctj_d = choices(macd < 0, param['pdd_macd'], macd > 0)
            pctj_d = pctj_d and choices(clo < mas, param['pdd_avg'], clo > mas)
            pctj_d = pctj_d and choices(mul < -1.5, param['pdd_yidong'], mul > 1.5)
            pctj_d = pctj_d and choices(cd < 0, param['pdd_chonghes'], cd > 0)
            pctj_d = pctj_d and choices(maidian < 0, param['pdd_chonghed'], maidian > 0)

            #pctj_k = (macd<0 and clo<mas)
            pctj_k = choices(macd < 0, param['pkd_macd'], macd > 0)
            pctj_k = pctj_k and choices(clo < mas, param['pkd_avg'], clo > mas)
            pctj_k = pctj_k and choices(mul < -1.5, param['pkd_yidong'], mul > 1.5)
            pctj_k = pctj_k and choices(cd < 0, param['pkd_chonghes'], cd > 0)
            pctj_k = pctj_k and choices(maidian < 0, param['pkd_chonghed'], maidian > 0)

            if reverse:
                kctj_d, kctj_k = kctj_k, kctj_d
                pctj_d, pctj_k = pctj_k, pctj_d

            if kctj_d and is_dk and self.dt_kc(datetimes):
                jg_d=clo
                startMony_d=clo
                str_time1=str(datetimes)
                is_d=1
                first_time = [str_time1,'多' ,clo]
                zsjg = low-clo-1 if zsjg2 >= -10 else zsjg
            elif kctj_k and is_dk and self.dt_kc(datetimes):
                jg_k=clo
                startMony_k=clo
                str_time2=str(datetimes)
                is_k=-1
                first_time = [str_time2, '空' ,clo]
                zsjg = clo-high-1 if zsjg2 >= -10 else zsjg

            if is_d==1:
                high_zs = high - startMony_d
                if high_zs >= ydzs:
                    _zsjg_d = startMony_d + high_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_d == 0:
                    _zsjg_d = startMony_d + zsjg  # 止损所在价格点
                if ((pctj_d or self.is_date(datetimes) or low<=_zsjg_d or high-startMony_d>=zyds) or qzpc) and str(datetimes) != str_time1:
                    res[dates]['duo'] += 1
                    price = round(_zsjg_d - startMony_d if low<=_zsjg_d else (zyds if high-startMony_d>=zyds else clo-startMony_d))
                    price -= cqdc
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time1, str(datetimes), '多', price])
                    is_d = 0
                    first_time = []
                    _zsjg_d = 0

            elif is_k==-1:
                low_zs = startMony_k - low
                if low_zs >= ydzs:
                    _zsjg_k = startMony_k - low_zs * 0.2  # 止损所在价格点，至少盈利20%
                elif _zsjg_k==0:
                    _zsjg_k = startMony_k - zsjg  # 止损所在价格点
                if ((pctj_k or self.is_date(datetimes) or high>=_zsjg_k or startMony_k-low>=zyds) or qzpc) and str(datetimes) != str_time2:
                    res[dates]['kong'] += 1
                    price = round(startMony_k - _zsjg_k if high>=_zsjg_k else (zyds if startMony_k-low>=zyds else startMony_k-clo))
                    price -= cqdc
                    res[dates]['mony'] += price
                    res[dates]['datetimes'].append([str_time2, str(datetimes), '空', price])
                    is_k = 0
                    first_time = []
                    _zsjg_k = 0


    def trd(self,_fa,reverse=False,_ma=60,param=None):
        ''' 交易记录 '''
        res={}
        da = self.zdata
        if len(da)>_ma:
            data2=self.vis(da=da[:_ma],ma=_ma)
            data2.send(None)
            da=da[_ma:]
            zsds, ydzs, zyds, cqdc = (param['zsds'], param['ydzs'], param['zyds'], param['cqdc']) if param else (
                                        100, 100, 200, 6)
            fa = self.xzfa[_fa](-zsds, ydzs, zyds, cqdc,reverse=reverse)
            fa.send(None)
        else:
            return
        is_date = str(datetime.datetime.now())[:15]
        for df2 in da:
            # df2格式：(Timestamp('2018-03-16 09:22:00') 31304.0 31319.0 31295.0 31316.0 275)
            dates=str(df2[0])[:10]
            if dates not in res:
                res[dates] = {'duo': 0, 'kong': 0, 'mony': 0, 'datetimes': [], 'dy': 0, 'xy': 0, 'ch': 0,}
            dt3=data2.send(df2)
            datetimes=dt3[-1]['datetimes']
            if _fa!="7" and ((datetimes.hour==16 and datetimes.minute>30) or datetimes.hour>16 or datetimes.hour<9):
                continue
            qzpc = True if (df2 == da[-1] and str(df2[0])[:15]!=is_date) else False
            res,first_time=fa.send((True,res,dt3,dates,qzpc))

        # sss=[]
        # for i in res:
        #     sss+=[j for j in res[i]['datetimes']]
        #with open(r"D:\tools\Tools\May_2018\2018-5-9\sss2.txt","w") as f:
        #    f.write(json.dumps(sss))
        #self.sendNone(data2)
        #self.sendNone(fa)

        return res,first_time

    def trd_all(self, _ma=60,reverse=True,param=None):
        fas = {}
        res = {}
        first_time = {}
        da = self.zdata
        if len(da) > _ma:
            data2 = self.vis(da=da[:_ma], ma=_ma)
            data2.send(None)
            da = da[_ma:]
            zsds, ydzs, zyds, cqdc = param['zsds'], param['ydzs'], param['zyds'], param['cqdc']
            for k, v in self.xzfa.items():
                fas[k] = v(-zsds, ydzs, zyds, cqdc,reverse=reverse)
                fas[k].send(None)
                res[k] = {}
        else:
            return
        is_date = str(datetime.datetime.now())[:15]
        for df2 in da:
            # df2格式：(Timestamp('2018-03-16 09:22:00') 31304.0 31319.0 31295.0 31316.0 275)
            dates = str(df2[0])[:10]
            dt3 = data2.send(df2)
            datetimes = dt3[-1]['datetimes']
            for fa in fas:
                if dates not in res[fa]:
                    res[fa][dates] = {'duo': 0, 'kong': 0, 'mony': 0, 'datetimes': [], 'dy': 0, 'xy': 0, 'ch': 0}
                if fa != "7" and ((datetimes.hour == 16 and datetimes.minute > 30) or datetimes.hour > 16 or datetimes.hour < 9):
                    continue
                qzpc = True if (df2 == da[-1] and str(df2[0])[:15] != is_date) else False
                try:
                    res[fa], first_time[fa] = fas[fa].send((True, res[fa], dt3, dates, qzpc))
                except Exception as exc:
                    pass

        # sss=[]
        # for i in res:
        #     sss+=[j for j in res[i]['datetimes']]
        # with open(r"D:\tools\Tools\May_2018\2018-5-9\sss2.txt","w") as f:
        #    f.write(json.dumps(sss))
        # self.sendNone(data2)
        # self.sendNone(fa)

        return res, first_time

    def trd_new(self,reverse=True,param=None):
        _ma = 60
        res = {}
        da = self.zdata
        if len(da) > _ma:
            data2 = self.vis(da=da[:_ma], ma=_ma)
            data2.send(None)
            da = da[_ma:]
            zsds, ydzs, zyds, cqdc = param['zsds'], param['ydzs'], param['zyds'], param['cqdc']
            fa = self.fa_new(-zsds, ydzs, zyds, cqdc, reverse=reverse, param=param)
            fa.send(None)
        else:
            return
        is_date = str(datetime.datetime.now())[:15]
        for df2 in da:
            # df2格式：(Timestamp('2018-03-16 09:22:00') 31304.0 31319.0 31295.0 31316.0 275)
            dates = str(df2[0])[:10]
            if dates not in res:
                res[dates] = {'duo': 0, 'kong': 0, 'mony': 0, 'datetimes': [], 'dy': 0, 'xy': 0, 'ch': 0}
            dt3 = data2.send(df2)
            datetimes = dt3[-1]['datetimes']
            if (datetimes.hour == 16 and datetimes.minute > 30) or datetimes.hour > 16 or datetimes.hour < 9:
                continue
            qzpc = True if (df2 == da[-1] and str(df2[0])[:15] != is_date) else False
            res, first_time = fa.send((True, res, dt3, dates, qzpc))

        return res, first_time


