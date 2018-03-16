import requests
import re
import pymysql
import time
import datetime


def get_data(url=None):
    '''获取恒生指数成分股数据，格式为：
    [(34, '腾讯控股'), (27, '香港交易所'), (21, '建设银行'), (18, '中国银行'), (16, '工商银行')...]'''
    weight_stock = ['汇丰控股', '恒生银行', '东亚银行', '香港交易所', '建设银行', '友邦保险',
                    '工商银行', '中国平安', '中银香港', '中国人寿', '交通银行', '中国银行',
                    '中电控股', '香港中华煤气', '电能实业', '华润电力', '长江基建集团',
                    '九龙仓集团', '恒基地产', '新鸿基地产', '新世界发展', '信和置业',
                    '恒隆地产', '中国海外发展', '领展房产基金', '华润置地', '长实集团',
                    '九龙仓置业', '碧桂园', '长和', "太古股份公司'A'", '银河娱乐',
                    '港铁公司', '招商局港口', '中国旺旺', '吉利汽车', '中信股份',
                    '万洲国际', '中国石油化工股份', '腾讯控股', '中国联通', '中国石油股份',
                    '中国海洋石油', '中国移动', '联想集团', '恒安国际', '中国神华',
                    '金沙中国有限公司', '瑞声科技', '蒙牛乳业', '舜宇光学科技']

    url = url if url else 'http://sc.hangseng.com/gb/www.hsi.com.hk/HSI-Net/HSI-Net?cmd=nxgenindex&index=00001&sector=00'
    req = requests.get(url).text
    req = re.sub('\s', '', req)
    # req=re.findall('<constituentscount="51">(.*?)</stock></constituents><isContingency>',req)
    com = re.compile('contribution="([+|-]*\d+)".*?<name>.*?</name><cname>(.*?)</cname></stock>')
    s = re.findall(com, req)
    # print(s)
    s = [(int(i[0]), i[1]) for i in s]
    result = []
    for w in weight_stock:
        sun = [i for i in s if i[1] == w]
        if len(sun) == 1:
            result.append(sun[0])
        elif len(sun) > 1:
            sun2 = [i for i in sun if i[0] != 0]
            if not sun2:
                sun2 = sun
            result.append(sun2[0])

    s2 = str(datetime.datetime.now())[:11]
    ti = re.findall('datetime="(.*?)"current', req)[0]
    if time.localtime().tm_mday!=int(ti[3:5]):
        return '',''
    s3 = s2 + ti[-8:]
    s3=datetime.datetime.strptime(s3.split('.')[0],'%Y-%m-%d %H:%M:%S')
    print(result)
    print(s3)
    if s3<datetime.datetime.now()-datetime.timedelta(minutes=10):
        return '',''
    return result, s3


conn = pymysql.connect(host='192.168.2.226', user='kairuitouzi', passwd='kairuitouzi', charset='utf8', port=3306,
                       db='stock_data')
cur = conn.cursor()


def insert_mysql():
    result, times = get_data()
    for res in result:
        try:
            cur.execute('insert into weight(number,name,time) values(%s,%s,%s)', (*res, times))
        except Exception as exc:
            print(exc)
    conn.commit()

if __name__ == '__main__':
    try:
        c=cur.execute('DELETE FROM weight WHERE TIME<"%s"'%str(datetime.datetime.now())[:10])
        print('清除历史记录：%d条'%c)
    except Exception as exc:
            print(exc)
    try:
        while 1:
            time.sleep(60)
            times=time.localtime()

            if (times.tm_hour==12 and times.tm_min>5) or (times.tm_hour==16 and times.tm_min>30) or times.tm_hour>16:
                continue
            
            if times.tm_hour>10 or (times.tm_hour==9 and times.tm_min>=20):
                insert_mysql()
            
            
    except Exception as exc:
            conn.close()
            print(exc)
