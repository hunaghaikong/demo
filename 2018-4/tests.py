def tests(l):
	print('Name','\t','Type(size)','\t','Value')
	for k,v in l.items():
		t=type(v)
		if t==int:
			print(k,'\t','int      ','\t',v)
		elif t==float:
			print(k,'\t','float    ','\t',v)
		elif t==bytes:
			print(k,'\t','bytes(%s)'%len(v),'\t',v[:20])
		elif t ==tuple:
			print(k,'\t','tuple(%s)'%len(v),'\t',v[:2])
		elif t==list:
			print(k,'\t','list (%s)'%len(v),'\t',v[:2])
		elif t==set:
			print(k,'\t','set  (%s)'%len(v),'\t',tuple(v)[:2])
		elif t==str:
			print(k,'\t','str  (%s)'%len(v),'\t',v[:20])
		elif t==dict:
			key=tuple(v.keys())
			print(k,'\t','dict (%s)'%len(v),'\t',{key[0]:v[key[0]],key[1]:v[key[1]]})
		else:
			print(k,'\t',type(v),'\t',v)


dd=123
def ss():
    a=1
    b=1.6
    c='abcd'
    e=(1,2,'4')
    f=['a',1,'c']
    g={'a':1,'b':2}
    h={1,2,'c'}
    i=b'abcd'
    j=dd+1
    tests(locals())

if __name__=='__main__':
    ss()
