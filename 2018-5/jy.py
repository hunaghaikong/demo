import time
import random
import pandas as pd


class HS:

    def get_data(self, file_name):
        dd = []
        for d in open(file_name, 'r'):
            d2 = d.split('\t')
            dd.append([d2[2], d2[3], d2[4], d2[9]])
        d = pd.DataFrame(dd[1:])
        d.columns = ['buy', 'sell', 'price', 'time']
        return d

    def datas(self):
        data = {
            'jy': 0,  # 交易手数
            'price': 0,  # 交易价格
            'cb': 0,  # 成本
            'start_time': 0,  # 开始时间
            'end_time': 0,  # 结束时间
            'mai': 0,  # 买卖
            'kc': [],  # 开仓
            'all_kp': [],  # 所有开平仓
            'pcyl': 0,  # 平仓盈利
            'pcyl_all':0, # 平仓盈利汇总
            'all_price': 0,  # 叠加价格
            'all': 0,  # 总盈亏
            'sum_price': 0,  # 全天叠加价格
            'all_jy_add': 0,  # 全天所有交易手数，叠加
            'dbs':0,   # 序号
            'wcds1': 0,
            'wcds': 0,  # 完成的单
        }
        ind = 0
        _while = 0
        while 1:
            msg=yield data,ind
            hand = int(msg[0]) if msg[0] else int(msg[1])
            if _while <= 0 and hand > 1:
                _while = hand
            _while -= 1
            if _while <= 0:
                ind += 1
            data['price'] = float(msg[2])
            if data['jy'] == 0:
                data['pcyl'] = 0
                data['wcds1'] = 0
                data['pcyl_all'] = 0


            if msg[0]:
                data['jy'] += 1
                data['all_jy_add'] += 1
                data['mai'] = 1
                data['all_price'] += data['price']
                data['sum_price'] += data['price']
                data['kc'].append([1, data['price']])
            elif msg[1]:
                data['jy'] -= 1
                data['all_jy_add'] += 1
                data['mai'] = -1
                data['all_price'] -= data['price']
                data['sum_price'] -= data['price']
                data['kc'].append([-1, data['price']])

            if len(data['kc']) > 1 and data['kc'][-1][0] != data['kc'][-2][0]:
                if data['kc'][-1][0] < 0:
                    data['pcyl'] = (data['kc'][-1][1] - data['kc'][-2][1])
                else:
                    data['pcyl'] = (data['kc'][-2][1] - data['kc'][-1][1])
                data['pcyl_all'] += data['pcyl']
                data['all'] += data['pcyl']
                data['kc'].pop()
                data['kc'].pop()
                data['wcds1'] += 1
                data['wcds'] += 1
            else:
                data['pcyl'] = 0

            if data['jy'] != 0:
                data['cb'] = data['all_price'] / data['jy']
            else:
                data['cb'] = 0  # 成本
                data['all_price'] = 0
            data['time'] = msg[-1]


    def ray(self,df,sxf=33.54):
        """ df:
                buy sell  price                 time
             0  1       30536  2018/05/02 09:16:53
            1   1       30559  2018/05/02 09:17:24
            """
        res = []
        ind=0
        dts=self.datas()
        dts.send(None)
        while ind<len(df.values):
            msg=df.values[ind]
            data,ind=dts.send(msg)
            pri = data['price']
            yscb=round(sum(i[-1] for i in data['kc'])/len(data['kc']),2) if len(data['kc'])>0 else 0  # 原始成本
            cb = round(data['cb'], 2)  # 成本
            jcbs=(data['wcds1']+abs(data['jy']))*sxf*2/50
            jcb = round(cb+jcbs,2) if data['jy']>0 else round(cb-jcbs,2) # 净成本
            # yl = round(-data['jy'] * (data['cb'] - pri), 2)  # 持仓盈利
            # cbyl = data['pcyl'] if data['jy'] == 0 else 0  # 此笔盈利
            pjyl = round(data['all'] / data['wcds'],2) if data['wcds']>0 else 0 # 平均盈利
            zcb = round(data['sum_price'] / data['jy'], 2) if data['jy'] != 0 else round(data['sum_price'], 2) # 持仓成本
            jzcbs=(data['wcds']+abs(data['jy']))*sxf*2/50
            jzcb = round(zcb+jzcbs,2)  # 净持仓成本
            res.append([data['time'],data['mai'], pri, data['jy'],yscb, cb,jcb, data['pcyl'], data['pcyl_all'], data['all'], pjyl, zcb,jzcb,
                        data['all']*50,data['all'] * 50 - sxf * data['all_jy_add'],round(sxf*data['all_jy_add'],2), data['wcds'], data['dbs']])
            data['dbs'] += 1 if data['jy'] == 0 else 0 # 序号

        res = pd.DataFrame(res)
        res.columns = ['时间','开仓', '当前价', '持仓','原始成本', '会话成本', '净会话成本', '此笔盈利', '会话盈利', '总盈利','平均盈利','持仓成本','净持仓成本','利润','净利润','手续费','已平仓','序号']
        return res

if __name__ == "__main__":
    h = HS()
    flod=r'D:\tools\Tools\May_2018\2018-5-7'
    xls=flod+'\\a.xls'
    dd=h.get_data(flod+'\\2018May11.txt')  # 2018May2.txt  2018May11.txt
    res=h.ray(dd)
    print(res)
    import os
    if os.path.isfile(xls):
        os.remove(xls)
    res.to_excel(xls)

