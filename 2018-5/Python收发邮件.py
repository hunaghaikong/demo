import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import getpass, imaplib

class Sarm:
	def send_email(self,from_addr, to_addr, subject, password):
	    msg = MIMEText("邮件正文,这是Python发送邮件测试的",'html','utf-8')
	    msg['From'] = u'<%s>' % from_addr
	    msg['To'] = u'<%s>' % to_addr
	    msg['Subject'] = subject

	    """
	    邮箱 	SMTP服务器 	SSL协议端口 	非SSL协议端口
		163 	smtp.163.com 	465或者994 	25
		qq 		smtp.11.com 	465或587 	25
		"""

	    smtp = smtplib.SMTP_SSL('smtp.163.com', 465)
	    smtp.set_debuglevel(1)
	    smtp.ehlo("smtp.11.com")
	    smtp.login(from_addr, password)
	    smtp.sendmail(from_addr, [to_addr], msg.as_string())

	def receive_email(self,user,password):
		M = imaplib.IMAP4()
		M.login(user,password) # (getpass.getuser(), getpass.getpass())
		M.select()
		typ, data = M.search(None, 'ALL')
		for num in data[0].split():
		    typ, data = M.fetch(num, '(RFC822)')
		    print ('Message %s\n%s\n' % (num, data[0][1]))
		M.close()
		M.logout()



if __name__ == "__main__":
    # 这里的密码是开启smtp服务时输入的客户端登录授权码，并不是邮箱密码
    # 现在很多邮箱都需要先开启smtp才能这样发送邮件
	from_addr = ''  # 发送邮箱
	to_addr = ''   # 接收邮箱
	password = ''  # 授权码
	subject = 'hello'  # 主题
	sarm=Sarm()
    sarm.send_email(from_addr,to_addr,subject,password)  # 发信
    sarm.receive_email(from_addr,password)				 # 收信
	
