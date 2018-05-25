import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options


import pymongo
#导入MongoDB

define("port", default=8001, help="run on the given port", type=int)
#定义监听的端口，随便挑个喜欢的数字吧

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
        (r"/", MainHandler),
        (r"/blog", BlogHandler),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        
        conn = pymongo.MongoClient(host="localhost", port=27017)  # 连接 MongoDB
        self.db = conn["blog"]
        tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html",)

    def post(self):
        import time
        title = self.get_argument("title", None)
        content = self.get_argument("content", None)
        blog = dict()
        if title and content:
            blog["title"] = title
            blog["content"] = content
            blog["date"] = int(time.time())
            print(blog)
            coll = self.application.db.blog
            coll.insert(blog)
            self.redirect("/blog")
        else:
            self.redirect("/")

class BlogHandler(tornado.web.RequestHandler):
    def get(self):
        coll = self.application.db.blog
        blog = coll.find_one()
        if blog:
            self.render("blog.html",
            page_title = blog["title"],
            blog = blog,
            )
        else:
            self.redirect("/")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()