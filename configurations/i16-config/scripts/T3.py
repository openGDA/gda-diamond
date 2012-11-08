def rfile(fname):
	DirPath="C:\gda\users\data\\"
	count=0
	strfloat=[]
	rfloat=[]
	while count < 20:
		li=linecache.getline(DirPath + fname,count+8).rstrip( )
		count +=1
		if len(li) <  2: 
			break
		strfloat.append(li.split("\t"))
	for ls in strfloat:
		nfloat=[]
		for lv in ls:
			nfloat.append(float(lv))
		rfloat.append(nfloat)
	return rfloat
