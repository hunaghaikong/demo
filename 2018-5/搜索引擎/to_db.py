import sys
from collections import deque
import urllib
from urllib import request
import re
from bs4 import BeautifulSoup
import lxml
import sqlite3
import jieba
from pyquery import PyQuery as pq


safelock=input('你确定要重新构建约5000篇文档的词库吗？(y/n)')
if safelock!='y':
    sys.exit('终止。')


url='http://www.iqiyi.com/' #'http://www.view.sdu.edu.cn/' # 'http://www.view.sdu.edu.cn'#入口  http://www.sdu.edu.cn

queue=deque()#待爬取链接的集合，使用广度优先搜索
visited=set()#已访问的链接集合
queue.append(url)

conn=sqlite3.connect('viewsdu.db')
c=conn.cursor()
#在create table之前先drop table是因为我之前测试的时候已经建过table了，所以再次运行代码的时候得把旧的table删了重新建
try:
    c.execute('drop table doc') # 删除表
    c.execute('create table doc (id int primary key,link text)')
    c.execute('drop table word') # 删除表
    c.execute('create table word (term varchar(25) primary key,list text)')
    conn.commit()
except:
    conn.close()

print('***************开始！***************************************************')
cnt=0

while queue:
    url=queue.popleft()
    visited.add(url)
    cnt+=1
    print('开始抓取第',cnt,'个链接：',url)

    #爬取网页内容
    try:
        response=request.urlopen(url).read()
        content=response.decode('gb18030') # gb18030
    except UnicodeDecodeError:
        try:
            content=response.decode('utf-8')
        except:
            continue
    except Exception as exc:
        print(exc)
        continue

    #寻找下一个可爬的链接，因为搜索范围是网站内，所以对链接有格式要求，这个格式要求根据具体情况而定
    
    #m=re.findall(r'<a href=\"([0-9a-zA-Z\_\/\.\%\?\=\-\&]+)\" target=\"_blank\">',content,re.I)
    #m2 = re.findall(r'<a href=\"(.*?)\".*?>',content,re.I)
    try:
        m = pq(content)('a').items()
    except:
        continue
    for a in m:
        i = a.attr('href')
        if i and ('javascript' not in i) and ('mailto:' not in i) and  len(i)>1:
            if ('www.' not in i) and ('http' not in i):
                i = url+'/'+i
            if (i not in visited) and (i not in queue):
                queue.append(i)
    # for x in m:
    #     if re.match(r'http.+',x):
    #         #if not re.match(r'http\:\/\/www\.view\.sdu\.edu\.cn\/.+',x):
    #         #    continue
    #         pass
    #     elif re.match(r'\/new\/.+',x):
    #         x=url + "new/" +x
    #     else:
    #         x=url + x
    #     if (x not in visited) and (x not in queue):
    #         queue.append(x)

    #解析网页内容,可能有几种情况,这个也是根据这个网站网页的具体情况写的
    soup=BeautifulSoup(content,'lxml')
    title=soup.title
    article=soup.find('div',class_='text_s',id='content')
    author=soup.find('div',class_='text_c')

    if title==None and article==None and author==None:
        print('无内容的页面。')
        continue

    elif article==None and author==None:
        print('只有标题。')
        title=title.text
        title=''.join(title.split())
        article=''
        author=''

    # elif title==None and author==None:
    #   print('只有内容。')
    #   title=''
    #   article=article.get_text("",strip=True)
    #   article=' '.join(article.split())
    #   author=''

    # elif title==None and article==None:
    #   print('只有作者。')
    #   title=''
    #   article=''
    #   author=author.find_next_sibling('div',class_='text_c').get_text("",strip=True)
    #   author=' '.join(author.split())

    # elif title==None:
    #   print('有内容有作者，缺失标题')
    #   title=''
    #   article=article.get_text("",strip=True)
    #   article=' '.join(article.split())
    #   author=author.find_next_sibling('div',class_='text_c').get_text("",strip=True)
    #   author=' '.join(author.split())

    elif article==None:
        print('有标题有作者，缺失内容')#视频新闻
        title=soup.h1.text
        title=''.join(title.split())
        article=''
        author=author.get_text("",strip=True)
        author=''.join(author.split())

    elif author==None:
        print('有标题有内容，缺失作者')
        title=soup.h1.text
        title=''.join(title.split())
        article=article.get_text("",strip=True)
        article=''.join(article.split())
        author=''

    else:
        title=soup.h1.text
        title=''.join(title.split())
        article=article.get_text("",strip=True)
        article=''.join(article.split())
        author=author.find_next_sibling('div',class_='text_c').get_text("",strip=True)
        author=''.join(author.split())

    print('网页标题：',title)

    #提取出的网页内容存在title,article,author三个字符串里，对它们进行中文分词
    seggen=jieba.cut_for_search(title)
    seglist=list(seggen)
    seggen=jieba.cut_for_search(article)
    seglist+=list(seggen)
    seggen=jieba.cut_for_search(author)
    seglist+=list(seggen)

    #数据存储
    conn=sqlite3.connect("viewsdu.db")
    c=conn.cursor()
    c.execute('insert into doc values(?,?)',(cnt,url))

    #对每个分出的词语建立词表
    for word in seglist:
        #print(word)
        #检验看看这个词语是否已存在于数据库
        c.execute('select list from word where term=?',(word,))
        result=c.fetchall()
        #如果不存在
        if len(result)==0:
            docliststr=str(cnt)
            c.execute('insert into word values(?,?)',(word,docliststr))
        #如果已存在
        else:
            docliststr=result[0][0]#得到字符串
            docliststr+=' '+str(cnt)
            c.execute('update word set list=? where term=?',(docliststr,word))
        print(docliststr,word)
    conn.commit()
    conn.close()
    print('词表建立完毕=======================================================')