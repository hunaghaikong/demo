
import pymysql
import json
import re
import configparser

config=configparser.ConfigParser()
config.read(r'D:\tools\Tools\EveryDay\demo\AndBefore_2018_3\conf.conf')

def get_conn(dataName):
    return pymysql.connect(db=dataName,user=config['U']['us'],passwd=config['U']['ps'],host=config['U']['hs'],charset='utf8')

def closeConn(conn):
    conn.commit()
    conn.close()

class MyUtil:
    def __init__(self):
        try:
            import redis
            pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
            self.r = redis.Redis(connection_pool=pool)  # 建立Redis连接(以连接池的方式)
        except:
            pass

    def getCode(self,rq_data):
        try:
            code_data=json.loads(self.r.get('stock_code'))
        except:
            conn=get_conn('stock_data')
            cur=conn.cursor()
            cur.execute('SELECT * FROM STOCK_CODE')
            code_data = cur.fetchall()
            conn.close()
            try:
                self.r.set('stock_code',json.dumps(code_data))
            except:
                pass
        res_data = [i for i in code_data if
                    rq_data in i[0] or rq_data in i[1] or rq_data in i[2] or (
                        rq_data in i[3] if i[3] else None) or rq_data in i[4]]
        try:
            for i in res_data:
                chd=i[0][:3]  #代码开头
                if chd=='600' or chd=='000' or chd=='300' or chd=='601' or chd=='002':
                    res_code=(i[-1]+i[0],i[1])
                    break
            else:
                for i in res_data:
                    if len(re.findall('\d',i[0]))>=5:
                        res_code=(i[-1]+i[0],i[1])
                        break
                    elif i[3]:
                        res_code = (i[-1] + i[3],i[1])
                        break
                else:    
                    res_code=None
        except:
            res_code=None
        return res_code


if __name__=='__main__':
    pass
