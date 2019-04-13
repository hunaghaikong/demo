
codes = "sh601226,sh600278"
price = "5.90,17.30"

s = """
<!DOCTYPE html>
<html>
<head>
	<title></title>
	<meta http-equiv="refresh" content="10">
</head>
<body>
<p>名称&nbsp;&nbsp;————&nbsp;&nbsp;价格&nbsp;&nbsp;&nbsp;&nbsp;最低&nbsp;&nbsp;&nbsp;&nbsp;最高&nbsp;&nbsp;&nbsp;&nbsp;幅度&nbsp;&nbsp;&nbsp;&nbsp;时间</p>
<div align="center" id="dataDiv"></div>
<script type="text/javascript" src="http://hq.sinajs.cn/list=%s" charset="UTF-8"></script>
 <script type="text/javascript">
function Wopen(strs){
	if(strs==''){ return '' }
   var winWidth=1140,winHeight=940;
   if (document.documentElement  && document.documentElement.clientHeight && document.documentElement.clientWidth){
      winWidth  = document.documentElement.clientWidth;
      winHeight = document.documentElement.clientHeight;
    }
  winWidth = winWidth-280+'px';
  winHeight = winHeight-150+'px';
  var specs = 'width=280,height=150,menubar=no,toolbar=no,status=no,scrollbars=yes, top='+winHeight+', left='+winWidth;

    myWindow = window.open('','_blank',specs);
    myWindow.document.write("<script>setTimeout('self.close()',5000);<\/script>");  
    myWindow.document.write(strs);
    myWindow.focus();
  };"""%(codes)

code2 = codes.split(',');
price2 = price.split(',')
len_price = len(price2)
pri = {}
for i in range(len(code2)):
	if i < len_price:
		pri[code2[i]] = price2[i]
	else:
		pri[code2[i]] = ''

s += "var wopens = '';"
title_n = ''
for code in code2:
	s += f'var {code} = hq_str_{code}.split(",");'
	s += f'document.write("<p><a target=_blank href=http://quote.eastmoney.com/{code}.html>"+{code}[0]+"</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+{code}[3]+"&nbsp;&nbsp;&nbsp;&nbsp;"+{code}[5]+"&nbsp;&nbsp;&nbsp;&nbsp;"+{code}[4]+"&nbsp;&nbsp;&nbsp;&nbsp;"+(({code}[3]-{code}[2])/{code}[2]*100).toFixed(2)+"&nbsp;&nbsp;&nbsp;&nbsp;"+{code}[31]+"</p>");'
	if(pri[code]):
		s += """if(%s[3]>%s){wopens += ('<p>'+%s[0]+' __ '+%s[3]+' __ '+((%s[3]-%s[2])/%s[2]*100).toFixed(2))+'<p>';}"""%(code,pri[code],code,code,code,code,code)
	title_n += f"{code}[0][0]+{code}[3]+' '+"

s += "Wopen(wopens);"
s += f"document.title={title_n[:-1]};"
s += "</script></body></html>"

with open('test.html','w') as f:
	f.write(s)


"""
var sh601258 = hq_str_sh601258.split(",");
var sz000001 = hq_str_sz000001.split(",");

document.write("<p>"+sh601258[0]+"&nbsp;&nbsp;&nbsp;&nbsp;"+sh601258[1]+"&nbsp;&nbsp;&nbsp;&nbsp;"+sh601258[2]+"&nbsp;&nbsp;&nbsp;&nbsp;幅度&nbsp;&nbsp;&nbsp;&nbsp;时间</p>");
document.write(hq_str_sz000001);
"""