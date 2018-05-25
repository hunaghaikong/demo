import zipfile
import time


def zipcrackl(files,list_mm):
	a = time.time()
	zfile = zipfile.ZipFile(files)
	for i in list_mm:
		try:
			zfile.extractall(pwd=i.encode())
			print('密码是：'+i)
			print('破解时间时：'+str(time.time()-a))
			break
		except:
			pass
	else:
		print('破解失败！建议加强字典！')

if __name__ == '__main__':
        with open('mm.txt','r') as f:
                mm = f.read()
        mm = mm.split()
        files = 'a.zip' # 
        zipcrackl(files,mm)
