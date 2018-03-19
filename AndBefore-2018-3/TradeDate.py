import requests
import re
import os
import time
import pickle
import MyUtil

"""
检查恒生指数断点时间
"""

def get_min_data(code='HSIc1'):
    '''
    :param code: Product name
    :return: Minute data that removes excess data
    '''
    conn = MyUtil.get_conn('stock_data')
    cur = conn.cursor()
    cur.execute(
        "SELECT DATETIME,OPEN,high,low,CLOSE,amount,vol FROM index_min WHERE CODE='%s' ORDER BY DATETIME" % code)
    mins = cur.fetchall()
    conn.close()
    mi = []

    def is_node(last, now):
        if last.hour == 11 and last.minute == 59 and now.hour == 12 and now.minute == 0:
            return 1
        elif last.hour == 16 and last.minute == 29 and now.hour == 16 and now.minute == 30:
            return 1
        elif last.hour == 23 and last.minute == 44 and now.hour == 23 and now.minute == 45:
            return 1
        return 0

    for i in range(len(mins)):
        if is_node(mins[i - 1][0], mins[i][0]):
            mi[-1][2] = mi[-1][2] if mi[-1][2] > mins[i][2] else mins[i][2]
            mi[-1][3] = mi[-1][3] if mi[-1][3] < mins[i][3] else mins[i][3]
            mi[-1][4] = mins[i][4]
            mi[-1][5] = mi[-1][5] + mins[i][5]
            mi[-1][6] = mi[-1][6] + mins[i][6]
        else:
            mi.append(list(mins[i]))
    m=0
    while 1:
        yield m
        m=mi

# Initializes generator
mi_init = get_min_data()
mi_init.send(None)

def getDate(size=300, code='hkHSI'):
    '''
    :param size: The most recent days to get
    :param code: Product name
    :return:Date list. example:['2017-12-01',。。。]
    '''
    fileName='getDate.txt'
    if os.path.isfile(fileName):
        times=time.localtime(os.path.getmtime(fileName))
        if times.tm_mday==time.localtime().tm_mday:
            with open(fileName,'rb') as f:
                s=pickle.load(f)
            return s
    s = requests.get(
        'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?_var=kline_dayqfq&param=%s,day,,,%s' % (code, size)).text
    s = re.findall('(\d\d\d\d-\d\d-\d\d)', s)
    s = list(set(s))
    s.sort()
    with open(fileName,'wb') as f:
        pickle.dump(s,f)
    return s


def mysql_date(code='HSIc1'):
    """
    :param code: Product name
    :return: Database date tuple. example:('2017-12-01',...)
    """
    conn = MyUtil.get_conn('stock_data')
    cur = conn.cursor()
    cur.execute("SELECT DATE_FORMAT(datetime,'%Y-%m-%d') FROM index_min WHERE CODE='{}' GROUP BY DATE_FORMAT(datetime,'%Y%m%d') ORDER BY datetime".format(code))
    dates = cur.fetchall()
    conn.close()
    dates = tuple(i[0] for i in dates)
    return dates


def mysql_min():
    """
    :return: Dictionaries of data bars corresponding to a database daily. example:{'2017-12-01':768,...}
    """
    conn = MyUtil.get_conn('stock_data')
    cur = conn.cursor()
    cur.execute(
        "SELECT DATE_FORMAT(datetime,'%Y-%m-%d'),COUNT(*) FROM index_min WHERE CODE='HSIc1' GROUP BY DATE_FORMAT(datetime,'%Y%m%d')")
    mins = cur.fetchall()
    conn.close()
    mins = {i[0]: i[1] for i in mins}
    return mins


def jcDate(date_sql):
    '''
    :param date_sql: Database date tuple. example:('2017-12-01',...)
    :return: A list of databases that do not exist on the day of the transaction. example['2017-12-01',...]
    '''
    dates = getDate()
    res = []
    index = dates.index(date_sql[0])
    for i in dates[index:]:
        if i not in date_sql:
            res.append(i)
    res.sort()
    return res


def jcTime(date_sql):
    '''
    :param date_sql: Database date tuple. example:('2017-12-01',...)
    :return: A list of data on the day,but incomplete minute data. example:[['2017-10-23', 358],...]
    '''
    mins = mysql_min()
    res_i = [[i, mins[i]] for i in date_sql if mins[i] != 768]

    return res_i


def turnover(size=6,mult=6,vols=1000):
    '''
    :param size: Minute data interval
    :param mult: The multiple of the previous volume
    :param vols: Minimum volume of volume
    :return: Data list of abnormal volume
    '''
    mi=mi_init.send(1)
    res_mi=[]
    for i in range(size,len(mi)):
        vol=0
        for j in range(i-size,i):
            vol+=mi[j][-1]
        if mi[i][-1]>vols and mi[i][-1]>vol/size*mult:
            res_mi.append(mi[i])
    return res_mi


def main():
    date_sql = mysql_date()
    res = jcDate(date_sql)
    res_i = jcTime(date_sql)
    print('全天没有数据：%d天，如下：' % len(res))
    print(res)
    print('当天分钟数据缺失：%d天，如下：' % len(res_i))
    print(res_i)

    mi = mi_init.send(1)
    print('去除1200、1630、2345等收盘点数据，并合并到了上一分钟，数据长度，和一条示例如下：')
    print(len(mi), mi[0])

    print('成交量异动：')
    abnormal_vol=turnover(mult=6,vols=2000)
    for i in abnormal_vol:
        print(str(i[0]),i)

if __name__ == '__main__':
    main()

