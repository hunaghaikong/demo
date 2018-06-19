from struct import unpack
import os
import sys
import time
import datetime
import win32api
import win32con
import win32gui
from collections import namedtuple, deque, OrderedDict

try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = os.path.join(BASE_DIR, 'AndBefore_2018_3')
    sys.path.append(BASE_DIR)
    from MyUtil import get_conn
except:
    from conn import get_conn

"""
读取文华财经dat数据，并存储到数据库
"""

# 启动文华财经
os.system('start C:\wh6模拟版\mytrader_wh.exe')

def transfer(files):
    contrast = None
    with open(files, 'rb') as f:
        buf = f.read()
    num = len(buf)
    no = (num - 4) / 36  # 32
    b = 4  # 0
    e = 40  # 32

    for i in range(int(no) - 1):
        a = unpack('iffffffff', buf[b:e])
        dd = a[0]
        openPrice = a[1]
        close = a[2]
        high = a[3]
        low = a[4]
        vol = a[5]
        amount = a[6]

        dd = time.localtime(dd)
        dd = datetime.datetime(*dd[:6])

        b += 36  # 32
        e += 36  # 32
        if i != 0:
            t = dd - contrast
            if dd < contrast or t.days > 100:
                break
            contrast = dd
            yield [dd, openPrice, high, low, close, vol, amount]
        else:
            contrast = dd
            yield [dd, openPrice, high, low, close, vol, amount]


def to_sql(conn, data):
    cur = conn.cursor()
    sql = "INSERT INTO wh_min(prodcode,datetime,open,high,low,close,vol) VALUES(%s,%s,%s,%s,%s,%s,%s)"
    count = 0
    cur.execute("SELECT prodcode,datetime FROM wh_min ORDER BY datetime DESC LIMIT 1")
    d = cur.fetchone()
    for i in data:
        try:
            cur.execute(sql, (i[0], i[1], i[2], i[3], i[4], i[5], i[6]))
        except Exception as exc:
            print(exc)
        count += 1
        if not count % 10000:
            conn.commit()
    else:
        conn.commit()
    conn.close()


def main(to_file=None):
    """ to_file: 如果有传入to_file，则只使用to_file这个文件更新数据库，否则检查所有指定文件并更新到数据库"""
    dirs = r'C:\wh6模拟版\Data\恒生期指\min1'
    N = namedtuple('N', ['month', 'code'])
    t = datetime.datetime.now()
    # 代码所对应的合约
    hsi = OrderedDict({
        '00034150.dat': N(1, 'HSIF8'),
        '00034151.dat': N(2, 'HSIG8'),
        '00034152.dat': N(3, 'HSIH8'),
        '00034154.dat': N(4, 'HSIJ8'),
        '00034155.dat': N(5, 'HSIK8'),
        '00034157.dat': N(6, 'HSIM8'),
        '00034158.dat': N(7, 'HSIN8'),
        '00034161.dat': N(8, 'HSIQ8'),
        '00034165.dat': N(9, 'HSIU8'),
        '00034166.dat': N(10, 'HSIV8'),
        '00034168.dat': N(11, 'HSIX8'),
        '00034170.dat': N(12, 'HSIZ8'),
    })

    conn = get_conn('carry_investment')
    cur = conn.cursor()
    cur.execute("SELECT prodcode,datetime FROM wh_min ORDER BY datetime DESC LIMIT 1")
    code_time = cur.fetchone()
    conn.commit()
    sql = "INSERT INTO wh_min(prodcode,datetime,open,high,low,close,vol) VALUES(%s,%s,%s,%s,%s,%s,%s)"

    numbers = [nu for nu in os.listdir(dirs) if nu in hsi and hsi[nu].month <= t.month]

    def runs(file_path):
        count = 0
        insert_size = 0
        code = hsi[file_path.split('\\')[-1]].code
        for i in transfer(file_path):
            if i[0] <= code_time[1]:
                continue
            try:
                cur.execute(sql, (code, str(i[0])[:19], i[1], i[2], i[3], i[4], i[5]))
                insert_size += 1
            except Exception as exc:
                print(exc)
            count += 1
            if not count % 10000:
                conn.commit()
        return insert_size

    if to_file:
        insert_size = runs(to_file)
        conn.commit()
        conn.close()
        return insert_size

    for number in numbers:
        file_path = dirs + os.sep + number
        insert_size = runs(file_path)

    conn.commit()
    conn.close()

    return insert_size

def sbdj(x,y,enter=None):
    """ 鼠标左击 与 按回车键 """
    win32api.SetCursorPos([x,y])    #为鼠标焦点设定一个位置
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)
    #win32api.keybd_event(0,0,win32con.KEYEVENTF_KEYUP,0)
    if enter is not None:
        # 按下回车键
        time.sleep(0.1)
        win32api.keybd_event(13,0,0,0)
        win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)

def get_ct():
    """ 获取所有Windows打开的窗体 """
    titles = set()
    def foo(hwnd, mouse):
        # 去掉下面这句就能获取所有，但是我不需要那么多
        if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
            titles.add(GetWindowText(hwnd))
    EnumWindows(foo, 0)
    return titles

def runs():
    """ 循环点击文华财经以刷新本地文件 """
    #time.sleep(12)
    DialogName = '赢顺云交易 － Ver6.7.810      文华云节点-模拟联通2      nymex'
    win = win32gui.FindWindow(None,DialogName)
    counts = 0
    while win == 0: # 若窗口没打开，则过一秒后再次检查
        time.sleep(1)
        win = win32gui.FindWindow(None,DialogName)
        counts += 1
    aj=OrderedDict({'wp':(16,330), 'wpzlhy':(906,999), 'hz=':(131,94), 'min1':(260,35), 'back_off':(19,31)})
    while 1:
        for i in aj:
            if i == 'back_off':
                time.sleep(10)
            sbdj(*aj[i])
        time.sleep(50)


if __name__ == '__main__':
    # res = main(d)
    # with open('res.txt','w') as f:
    #	f.write(json.dumps(res))
    # to_sql(conn,res[:-1])
    main()
