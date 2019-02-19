from ctypes import *
import time


class User32:

    def __init__(self):
        self.user = windll.user32

    def box(self):
        """ 弹出确认框，是：6，否：7，取消：2 """
        return self.user.MessageBoxW(None, '现在已经12点了，该吃饭了！', '消息提示', 3)

    def close_screen(self):
        """ 关闭电脑屏幕 """
        wn_syscommand = 0x0112
        sc_monitorpower = 0xf170
        HWND_BROAOCAST = self.user.FindWindowExA(None, None, None, None)
        self.user.SendMessageA(HWND_BROAOCAST, wn_syscommand, sc_monitorpower, 2)

    def lock_screen(self):
        """ 锁屏 """
        self.user.LockWorkStation()


if __name__ == '__main__':
    u32 = User32()
    t = time.localtime().tm_hour
    while 1:
        t2 = time.localtime().tm_hour
        if 8 > t or t > 17:
            u32.close_screen()
            time.sleep(60 * 60)
            continue
        if t == t2:
            time.sleep(60 * 5)
            continue
        t = t2
        if t2>=17:
        	for i in range(30):
        		u32.close_screen()
        		time.sleep(2)
        else:
	        for i in range(60):
	            u32.close_screen()
	            time.sleep(2)
