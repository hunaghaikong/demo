#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:05
# @Author  : Hadrianl 
# @File    : util.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

"""
该文件存储一些基本的数据获取的字段名转换和基本的数据整理函数
"""
import datetime
from dateutil.parser import parse
import configparser
from pandas import Timestamp
import logging.config
import os
import math
import pymongo

from DataIndex import ZB

server_conf = configparser.ConfigParser()
server_conf.read(os.path.join('conf', 'server.conf'))

# 服务器的MYSQL
KAIRUI_MYSQL_HOST = server_conf.get('MYSQL', 'host')
KAIRUI_MYSQL_PORT = server_conf.getint('MYSQL', 'port')
KAIRUI_MYSQL_USER = server_conf.get('MYSQL', 'user')
KAIRUI_MYSQL_PASSWD = server_conf.get('MYSQL', 'password')
KAIRUI_MYSQL_DB = server_conf.get('MYSQL', 'db')

KAIRUI_DB_TYPE = server_conf.get('DATABASE', 'databasetype')

# 订阅数据的host与port
ZMQ_SOCKET_HOST = server_conf.get('ZMQ_SOCKET', 'host')
ZMQ_TICKER_PORT = server_conf.getint('ZMQ_SOCKET', 'ticker_port')
ZMQ_PRICE_PORT = server_conf.getint('ZMQ_SOCKET', 'price_port')
ZMQ_INFO_PORT = server_conf.getint('ZMQ_SOCKET', 'info_port')

# 合约名称
CONTRACT_NAME = server_conf.get('CONTRACT_NAME','name')
SYMBOL = server_conf.get('CONTRACT_NAME','symbol')

# 方案名称
SCHEME_NAME = server_conf.get('SCHEME_NAME','name')

# 日志的配置
logging.config.fileConfig(os.path.join('conf', 'log.conf'), disable_existing_loggers=False)
A_logger = logging.getLogger('root')
F_logger = logging.getLogger('root.data_fetch')
H_logger = logging.getLogger('root.data_handle')
V_logger = logging.getLogger('root.data_visualize')
S_logger = logging.getLogger('server_info')


MA_COLORS = {'_ma10': (255, 255, 255),
             '_ma20': (129, 255, 8),
             '_ma30': (182, 128, 219),
             '_ma60': (255, 0, 0)}

MONTH_LETTER_MAPS = {1: 'F',
                     2: 'G',
                     3: 'H',
                     4: 'J',
                     5: 'K',
                     6: 'M',
                     7: 'N',
                     8: 'Q',
                     9: 'U',
                     10: 'V',
                     11: 'X',
                     12: 'Z'
                     }


# 确定需要展示的K线范围
def date_range(type_, **kwargs):
    """
    初始化展示日期
    :param type_: 'present'为当前行情，'history'
    :param kwargs: type为'present'时，bar_num为1min的bar条数
                 type为'history'时，start为开始的分钟，end为结束的分钟,bar_num为偏移的分钟数
    :return: start_time, end_time
    """
    if type_ == 'present':
        min_bar = kwargs['bar_num']
        start_time = datetime.datetime.now() - datetime.timedelta(minutes=min_bar)
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=10)
    elif type_ == 'history':
        if kwargs.get('bar_num'):
            t_delta = datetime.timedelta(minutes=kwargs.get('bar_num'))
            start_time = parse(kwargs['start']) if kwargs.get('start') else parse(kwargs['end']) - t_delta
            end_time = parse(kwargs['end']) if kwargs.get('end') else parse(kwargs['start']) + t_delta
        elif kwargs.get('start', None) and kwargs.get('end', None):
            start_time = parse(kwargs['start'])
            end_time = parse(kwargs['end'])
    else:
        raise ValueError('type 类型错误')
    A_logger.info(f'初始化{type}数据数据范围:<{start_time}>-<{end_time}>')
    return start_time, end_time


def symbol(code_prefix, type_='futures', **kwargs):
    if type_ == 'futures':
        m_code = MONTH_LETTER_MAPS[kwargs.get('month')] if kwargs.get('month') else MONTH_LETTER_MAPS[datetime.datetime.now().month]
        y_code = kwargs['year'][-1] if kwargs.get('year') else str(datetime.datetime.now().year)[-1]
        Symbol = code_prefix + m_code + y_code  # 根据当前时间生成品种代码
        A_logger.info(f'初始化symbol代码-{Symbol}')
        return Symbol


def print_tick(new_ticker):
    print(f'tickertime: {new_ticker.TickerTime}-price: {new_ticker.Price}-qty: {new_ticker.Qty}')


def help_doc():
    text = f'''主要命名空间：ohlc, tick_datas,trade_datas, win
    ohlc是数据类的历史K线数据；tick_datas是数据类的当前K线数据(包括当前k线内的tick数据）；
    trade_datas是交易数据；win是可视化类的主窗口
    主要用法：
    ohlc.data-历史K线数据
    ohlc.indicator-历史K线指标数据
    ohlc.open-历史K线open
    ohlc.high-历史K线high
    ohlc.low-历史K线low
    ohlc.close-历史K线close
    ohlc.datetime-历史K线时间
    ohlc.timestamp-历史K线时间戳
    ohlc.timeindex-历史k线时间序列
    '''
    print(text)
    return

class Zbjs(ZB):
    def __init__(self,df):
        super(Zbjs, self).__init__()
        time1=df.values[0][0]
        time2=df.values[-1][0]
        import pymysql
        conn = pymysql.connect(host=KAIRUI_MYSQL_HOST, user=KAIRUI_MYSQL_USER,password=KAIRUI_MYSQL_PASSWD, charset='utf8',db='carry_investment')
        cur=conn.cursor()
        sql = "SELECT DATETIME,OPEN,high,low,CLOSE,vol FROM wh_same_month_min WHERE prodcode='HSI' AND datetime>='{}' AND datetime<='{}'".format(time1, time2)
        cur.execute(sql)
        self.zdata = cur.fetchall()  # [(d[0], d[1], d[2], d[3], d[4]) for d in df.values]
        #print(self.zdata)

    def get_doc(self,fa):
        return self.fa_doc.get(fa)

    def is_date(self,datetimes):
        ''' 是否已经或即将进入晚盘 '''
        h=datetimes.hour
        return (h==16 and datetimes.minute>=29) or h>16 or h<9

    def main2(self,_fa,_ma=60):
        res,first_time = self.trd(_fa=_fa,_ma=_ma)
        res2 = [res[i]['datetimes'] for i in res]
        buysell = {}
        for day in res2:
            for i in day:
                if i:
                    buysell[Timestamp(i[0])] = 1 if i[2] == '多' else -1
                    buysell[Timestamp(i[1])] = 2 if i[2] == '空' else -2
        return buysell


class MongoDBData:
    """ MongoDB 数据库的连接与数据查询处理类 """


    def __init__(self, db=None, table=None):
        self.db_name = db
        self.table = table
        # if not self._coll:
        #     self._coll = self.get_coll()
        self._coll = self.get_coll()

    def get_coll(self):
        client = pymongo.MongoClient('mongodb://192.168.2.226:27017')
        self.db = client[self.db_name] if self.db_name else client['HKFuture']
        coll = self.db[self.table] if self.table else self.db['future_1min']
        return coll

    def get_hsi(self, sd, ed, code='HSI'):
        """
        获取指定开始日期，结束日期，指定合约的恒指分钟数据
        :param sd: 开始日期
        :param ed: 结束日期
        :param code: 合约代码
        :return:
        """
        # hf = HKFuture()
        # if not isinstance(sd, str):
        #     sd = dtf(sd)
        # if not isinstance(ed, str):
        #     ed = dtf(ed)
        # data = hf.get_bars(code, start=sd, end=ed)
        # for t, _, o, h, l, c, v in data.values:
        #     yield [t, o, h, l, c, v]

        if isinstance(sd, str):
            sd = datetime.datetime.strptime(sd,'%Y-%m-%d %H:%M:%S')
        if isinstance(ed, str):
            ed = datetime.datetime.strptime(ed,'%Y-%m-%d %H:%M:%S')
        dates = set()
        start_dates = [sd]
        _month = sd.month
        _year = sd.year
        e_y = ed.year
        e_m = ed.month
        _while = 0
        res = []
        while _year < e_y or (_year == e_y and _month <= e_m):
            _month = sd.month + _while
            _year = sd.year + math.ceil(_month / 12) - 1
            _month = _month % 12 if _month % 12 else 12
            code = code[:3] + str(_year)[2:] + ('0' + str(_month) if _month < 10 else str(_month))
            try:
                _ed = self.db['future_contract_info'].find({'CODE': code})[0]['EXPIRY_DATE']
            except:
                return res
            if _ed not in start_dates:
                start_dates.append(_ed)
            _while += 1
            if sd >= _ed:
                continue
            _sd = start_dates[-2]

            if _sd > ed:
                return res
            data = self._coll.find({'datetime': {'$gte': _sd, '$lt': _ed}, 'code': code},
                                   projection=['datetime', 'open', 'high', 'low', 'close']).sort('datetime',1)  # 'HSI1808'

            _frist = True
            for i in data:
                date = i['datetime']
                if _frist:
                    _frist = False
                    exclude_time = str(date)[:10]
                    dates.add(datetime.datetime.strptime(exclude_time + ' 09:14:00', '%Y-%m-%d %H:%M:%S'))
                    dates.add(datetime.datetime.strptime(exclude_time + ' 12:59:00', '%Y-%m-%d %H:%M:%S'))
                if date not in dates:
                    dates.add(date)
                    if date > ed:
                        return res
                    res.append([date, i['open'], i['high'], i['low'], i['close']])
        return res