import time
import json
import datetime
import requests
from pyquery import PyQuery
from threading import Thread


"""
博彩网站数据，套利统计
"""


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
THIS_DATE = str(datetime.datetime.now())[:10]


res1 = []
res2 = []
res3 = []


def get_landing(page=0):
	# url='https://landing-sb.prdasbb18a1.com/en-gb/Service/CentralService?GetData&ts='+str(int(time.time()*1000))
	url='https://landing-sb.prdasbb18a1.com/zh-cn/Service/CentralService?GetData&ts='+str(int(time.time()*1000))

	ss = {
		'today': '/zh-cn/sports/football/matches-by-date/today/full-time-asian-handicap-and-over-under',		# 今日赛事
		'tomorrow': '/zh-cn/sports/football/matches-by-date/tomorrow/full-time-asian-handicap-and-over-under',	# 明日赛事
		'all': '/zh-cn/sports/football/competition/full-time-asian-handicap-and-over-under',					# 所有赛事
		}

	res_frist = []
	for page in range(3000):
		post_data = {
			'CompetitionID': -1,
			'IsEventMenu': False,
			'IsFirstLoad': True,
			'LiveCenterEventId': 0,
			'LiveCenterSportId': 0,
			'SportID': 1,
			'VersionF': -1,
			'VersionH': 0,
			'VersionL': -1,
			'VersionS': -1,
			'VersionT': -1,
			'VersionU': 0,
			'oIsFirstLoad': True,
			'oIsInplayAll': False,
			'oOddsType': 0,
			'oPageNo': page,
			'oSortBy': 1,
			'reqUrl': ss['all'],
		}


		d = requests.post(url,data=post_data,headers=headers).text
		d = json.loads(d)


		# 获得分类
		# res = []
		# res_dt = {}

		# for i in d['lpd']['psm']['psmd']:
		# 	name = i['sen']
		# 	yname = i['sn']
		# 	for j in i['puc']:
		# 		t_name = j['cn']
		# 		for v in j['ces']:
		# 			res.append((name,yname,t_name,v['at'],v['eid'],v['en'],v['esd'],v['est'],v['ht']))
		# 			res_dt[v['eid']] = (name,yname,t_name,v['at'],v['eid'],v['en'],v['esd'],v['est'],v['ht'])



		res_pl = []

		for i in d['mod']['d']:
			name = i['n']
			for j in i['c']:
				t_name = j['n']
				for v in j['e']:
					try:
						x2st = v['o'].get('1x21st',())
						if x2st:
							x2st = (float(x2st[1]),float(x2st[5]),float(x2st[3]))
						x1x = v['o'].get('1x2',())
						if x1x:
							x1x = (float(x1x[1]),float(x1x[5]),float(x1x[3]))
						_id = v['k']
						_z = v['i'][0]
						_k = v['i'][1]
						address = f"https://www.18x8bet.com/zh-cn/sports/{_id}/{_z}-vs-{_k}"
						if x1x:
							res_pl.append((name,t_name,_id,v['edt'].replace('T',' '),_z,_k,{'1x21st':x2st,'1x2':x1x},address))
					except:
						pass
		if res_pl and res_frist == res_pl:
			return
		res1.extend(res_pl)
		res_frist = res_pl



def get_marathonbet(page=0):

	res_frist = []

	for page in range(3000):
		try:
			url = f'https://www.marathonbet.com/zh/betting/Football/?page={page}&pageAction=getPage&_='+str(int(time.time()*1000))
			d = requests.get(url).text
			d = json.loads(d)

			d2=d[0]['content']
			d3=PyQuery(d2)
			divs=d3('div')



			date_dt = {
				'一月': '01', 'Jan': '01',
				'二月': '02', 'Feb': '02',
				'三月': '03', 'Mar': '03',
				'四月': '04', 'Apr': '04',
				'五月': '05', 'May': '05',
				'六月': '06', 'Jun': '06',
				'七月': '07', 'Jul': '07',
				'八月': '08', 'Aug': '08',
				'九月': '09', 'Sep': '09',
				'十月': '10', 'Oct': '10',
				'十一月': '11', 'Nov': '11',
				'十二月': '12', 'Dec': '12',
				}

			res = []

			for i in divs:
				if i.attrib.get('data-event-page'):
					# name = i.attrib['data-event-name']
					_ads = i.attrib['data-event-page']
					# _a = _ads.split('/')[-2].split('+')
					address = 'https://www.marathonbet.com' + _ads
					i = PyQuery(i)
					trs=i('table tbody tr')
					# trs=[tr for tr in trs if tr.attrib]
					for tr in trs:
						tr = PyQuery(tr)
						span = tr('span')
						_date = tr('.date').text()
						_date = _date.strip()
						if _date[3:5] in date_dt:
							_date = str(time.localtime().tm_year) + '-' + date_dt[_date[3:5]] + '-' + _date[:2] + ' ' + _date[-5:] + ':00'
						if len(_date) == 5:
							_date = THIS_DATE+' '+_date+':00'
						v = [i.text for i in span]
						if len(v) > 13:
							res.append((v[0],v[1],_date,float(v[4]),float(v[6]),float(v[5]),float(v[11]),float(v[13]),float(v[12]),address))
			if res_frist == res:
				return 
			res2.extend(res)
			res_frist = res
		except Exception as exc:
			print(exc)
			return 



def get_bwin9828():
	bsUrl = 'https://www.bwin9828.com'
	url = 'https://www.bwin9828.com/zh-cn/sport/football'
	h = requests.get(url,headers=headers).text
	h2 = PyQuery(h)
	h3 = h2('.coupon-homepage__group-link')
	res2 = []
	for i in h3:
		title = i.attrib['title']
		n_url = bsUrl + i.attrib['href']
		nh = requests.get(n_url, headers=headers).text
		nh2 = PyQuery(nh)
		divs = nh2('.multiple_markets')
		
		for div in divs:
			div=PyQuery(div)
			qcbc = div('h4')[0].attrib.get('title','')
			if '90分钟' in qcbc:
				qcbc = '1x2'
			elif '上半场' in qcbc:
				qcbc = '1x21st'
			if qcbc in {'1x2','1x21st'}:
				nh3 = div('.body')
				for j in nh3:
					try:
						if j.attrib.get('data-market-cash-out-elegible'):
							j=PyQuery(j)
							tds=j('td')
							td0 = PyQuery(tds[0])
							span = td0('span')
							dts = str(datetime.datetime.fromtimestamp(int(span.attr('data-time'))/1000))
							td1 = PyQuery(tds[1])
							a = td1('a')
							n_title = a.attr('title')
							href = a.attr('href')
							td2 = PyQuery(tds[2])
							span2 = td2('span')
							price_1 = float(span2.attr('data-price'))
							td3 = PyQuery(tds[3])
							span3 = td3('span')
							price_x = float(span3.attr('data-price'))
							td4 = PyQuery(tds[4])
							span4 = td4('span')
							price_2 = float(span4.attr('data-price'))
							name = n_title.split('v')
							res3.append((title,name[0].strip(),name[1].strip(),dts,price_1,price_x,price_2,qcbc,bsUrl+href))
							# res2[bsUrl+href] = (title,name[0].strip(),name[1].strip(),dts,price_1,price_x,price_2,bsUrl+href)
					except:
						pass



def hlzh(x,y,z):
	""" 盈利空间 与 投注比例计算 """
	# if isinstance(x,str):
	# 	x = float(x)
	# if isinstance(y,str):
	# 	y = float(y)
	# if isinstance(z,str):
	# 	z = float(z)
	
	cou = x+y+z
	x1,y1,z1 = cou/x,cou/y,cou/z
	cou1 = x1+y1+z1
	x2,y2,z2 = round(x1/cou1*100,3),round(y1/cou1*100,3),round(z1/cou1*100,3)

	return round(x*x2/(x2+y2+z2),3),(x2,y2,z2)





t1 = Thread(target=get_landing)
t2 = Thread(target=get_marathonbet)
t3 = Thread(target=get_bwin9828)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()


r1={i[4]:i for i in res1}
r2={i[0]:i for i in res2}
r3={i[1]:i for i in res3 if i[7]=='1x2'}

# r11 = {i[5]:i for i in res1}
# r22 = {i[1]:i for i in res2}
# r33 = {i[2]:i for i in res3 if i[7]=='1x2'}
sss = []
res = []
for i in r1:
	if i in r2 and i in r3:
		r1_time = str(datetime.datetime.strptime(r1[i][3],'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours=12))
		if r1_time == r2[i][2] == r3[i][3]:
			_r1 = r1[i][6]['1x2']
			c1 = {_r1[0]:r1[i][-1],r2[i][3]:r2[i][-1],r3[i][4]:r3[i][-1]}
			cx = {_r1[1]:r1[i][-1],r2[i][4]:r2[i][-1],r3[i][5]:r3[i][-1]}
			c2 = {_r1[2]:r1[i][-1],r2[i][5]:r2[i][-1],r3[i][6]:r3[i][-1]}
			mc1,mcx,mc2 = max(c1),max(cx),max(c2)
			gl,zh = hlzh(mc1,mcx,mc2)
			sss.append(gl)
			if gl>1:
				res.append((gl,(mc1,mcx,mc2),zh,(c1[mc1],cx[mcx],c2[mc2])))
	if i in r2:
		r1_time = str(datetime.datetime.strptime(r1[i][3],'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours=12))
		if r1_time == r2[i][2]:
			_r1 = r1[i][6]['1x2']
			c1 = {_r1[0]:r1[i][-1],r2[i][3]:r2[i][-1]}
			cx = {_r1[1]:r1[i][-1],r2[i][4]:r2[i][-1]}
			c2 = {_r1[2]:r1[i][-1],r2[i][5]:r2[i][-1]}
			mc1,mcx,mc2 = max(c1),max(cx),max(c2)
			gl,zh = hlzh(mc1,mcx,mc2)
			sss.append(gl)
			if gl>1:
				res.append((gl,(mc1,mcx,mc2),zh,(c1[mc1],cx[mcx],c2[mc2])))
	elif i in r3:
		r1_time = str(datetime.datetime.strptime(r1[i][3],'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours=12))
		if r1_time == r3[i][3]:
			_r1 = r1[i][6]['1x2']
			c1 = {_r1[0]:r1[i][-1],r3[i][4]:r3[i][-1]}
			cx = {_r1[1]:r1[i][-1],r3[i][5]:r3[i][-1]}
			c2 = {_r1[2]:r1[i][-1],r3[i][6]:r3[i][-1]}
			mc1,mcx,mc2 = max(c1),max(cx),max(c2)
			gl,zh = hlzh(mc1,mcx,mc2)
			sss.append(gl)
			if gl>1:
				res.append((gl,(mc1,mcx,mc2),zh,(c1[mc1],cx[mcx],c2[mc2])))

for i in r2:
	if i in r3:
		if r2[i][2] == r3[i][3]:
			c1 = {r2[i][3]:r2[i][-1],r3[i][4]:r3[i][-1]}
			cx = {r2[i][4]:r2[i][-1],r3[i][5]:r3[i][-1]}
			c2 = {r2[i][5]:r2[i][-1],r3[i][6]:r3[i][-1]}
			mc1,mcx,mc2 = max(c1),max(cx),max(c2)
			gl,zh = hlzh(mc1,mcx,mc2)
			sss.append(gl)
			if gl>1:
				res.append((gl,(mc1,mcx,mc2),zh,(c1[mc1],cx[mcx],c2[mc2])))

res.sort(key=lambda x:x[0])
res.reverse()

