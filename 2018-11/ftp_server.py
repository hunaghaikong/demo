from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def ftp_server(host, port, user, password, path=r'D:\ftp'):
    """ FTP 服务端 """
    # 实例化虚拟用户，这是FTP验证首要条件
    authorizer = DummyAuthorizer()

    # 添加用户权限和路径，括号内的参数是(用户名， 密码， 用户目录， 权限)
    authorizer.add_user(user, password, path, perm='elradfmw')

    # 添加匿名用户 只需要路径
    authorizer.add_anonymous(path)

    # 初始化ftp句柄
    handler = FTPHandler
    handler.authorizer = authorizer

    # 添加被动端口范围
    handler.passive_ports = range(2000, 2333)

    # 监听ip 和 端口
    server = FTPServer((host, port), handler)  # ('192.168.2.204', 2121)

    # 开始服务
    server.serve_forever()


if __name__ == '__main__':
    host = '192.168.2.204'  # IP
    port = 2121  # 端口
    user = 'user'  # 用户名
    password = '123456'  # 密码
    path = r'D:\ftp'  # 用户目录
    ftp_server(host, port, user, password, path)
