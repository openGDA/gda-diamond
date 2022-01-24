##from java.lang import exception???? not needed
def scancn(*params):
	'''
	scancn dev1 step1 n1 step2 n2 ... dev2 ...
	centred scan. Syntax as per scan except that first device in list is
	given a step size and number of scan intervals (no. of points + 1)
	A series of these is given for multidimensional scans
	The first device in the list is scanned about it's current position and 
	returned to start position after scan
	Example: 'scancn x .1 4 ct3 1' is equivalent to scan x x()-.2 x()+.2 .1 ct3 1'
	where x() is the current position of x
	'''

	# create lists of devices and parameters
	devlist=[]; paramlist=[];
	for token in params:
		if isinstance(token, Scannable):			#parameter is a device
			if not(devlist==[]):				#if device list not empty...
				paramlist+=[currentlist];		#append list of device parameters to parameter list for previous device
			currentlist=[];					#reset current list
			devlist=devlist+[token]; 			#append new device to device list
		elif isinstance(token, (int, float, list)):		#paramemer is a number
			currentlist+=[token];				#add parameter to current parameter list
		else:
			raise TypeError('=== Parameter must be a ScannableMotionBase, number or list. Found {}'.format(type(token)))
	paramlist+=[currentlist];					#append last one to list	


	dim=len(paramlist[0])/2					#dimension of scan
	if 2*dim!=len(paramlist[0]):					#wrong number of params
		raise ValueError("=== Wrong number of parameters for first pd")

	p0old=paramlist[0]						#params for first PD (the only one to modify)
	pd0=devlist[0]							#first PD (only one ised for centring)
#	pd0pos=pd0()							#get current position of first PD
	try:
		pd0pos=list(pd0[:])			#list converts to list. remove when bug fixed							#get current position (input parameters) of first PD

		if len(pd0pos)==1:			#this line not needed if bug fixed. 
			pd0pos=pd0pos[0]		#this line not needed if bug fixed
	except:
		pd0pos=pd0[:]

#	print pd0pos

#	print 'pd0pos', pd0pos
	scanrange=mult(pd0pos,0);					#zero vector of correct size
#	print 'scanrange',scanrange
	for n in range(0,dim*2-1,2):
		scanrange=add(scanrange, mult(p0old[n],(p0old[n+1])))	#loop through each step/n and calc scan range vector


	p0new=(2+dim)*[0];						#zero vector for new parameters
	p0new[0]=add(pd0pos,mult(-0.5,scanrange));			#start position=current-range/2
	p0new[1]=add(pd0pos,mult(0.5,scanrange));			#end position=current+range/2
	p0new[2:]=p0old[0::2];						#step sizes
	paramlist[0]=p0new;						#write re-packaged paramters back to list	

	full_list=[]; full_name_list=[];				#new list for scan or printing (use name for printing)
	for n in range(len(devlist)):
#		print 'devlist[n]', [devlist[n]]
		full_list+=[devlist[n]]
		full_name_list+=[devlist[n].getName()]
#		print 'full_name_list', full_name_list
		if paramlist[n]!=[]:					#do not append if empty list
			full_list+=paramlist[n]
			full_name_list+=paramlist[n]

#	print 'full_list', full_list
	print 'full_name_list', full_name_list
	try:
		scan(full_list)							#do scan
	except InterruptedException,e:					#move to start only following stop button press
		print "=== Problem with scan or halt button pressed"	
		print '=== Moving ', pd0.getName(),' back to start'
		print pd0(pd0pos);							#move back to start	
		print '=== Done - now aborting script if necessary'
		raise
	
	print '=== Moving ', pd0.getName(),' back to start'
	print pd0(pd0pos);							#move back to start	
	print '=== Done'

	#get cen value assuming first PD in scan list is x and last collumn of the last PD is y
	pdx=devlist[0];
	pdy=devlist[-1];
	maxval=FindScanPeak((pdy.getInputNames()+pdy.getExtraNames())[-1]);	#last collumn of pdy
	print 'max=',maxval

	print pdx.getInputNames()
	xval_at_y_peak=[] 							#assume vector (input) device
	for in_name in pdx.getInputNames():
		xval_at_y_peak+=[maxval[in_name]]
	if len(xval_at_y_peak)==1:
		xval_at_y_peak=xval_at_y_peak[0]				#return scalar if single element list
	print xval_at_y_peak	#need to set global

def add(*items):
	#add  list objects containing lists of lists and numbers. arrays must be same size or scalar
	allscalars=1; somescalars=0; listsize=1; newitems=[];
	for item in items:
		newitems+=[item]				#add item to newitems list
		if isinstance(item,(int, float)):		#numerical objects
			somescalars=1;
		else:
			if len(item)==1:
				newitems[-1]=item[0];		#convert single element list to component object and replace last element in newitems list
				somescalars=1;
			else:
				allscalars=0;			#not all scalars
				if listsize==1:
					listsize=len(item);
				if listsize!=len(item):
					print "=== Inconsistent shape"
					raise
	if allscalars==1:					#all scalars so add
		tot=0;
		for item in newitems:
			tot=tot+item				#add as scalars
		return tot
	if somescalars==1:
		for i in range(len(newitems)):
			try:
				len(newitems[i]);		#will fail if not item with length
			except:
				newitems[i]=[newitems[i]]*listsize;	#pad out scalars to fit lists e.g. 1=>[1,1,1]
	result=(newitems[0])[:];					#remove bracket after bug fix? use [:] to avoid copy by reference
	for i in range(len(result)):
		for item in newitems[1:]:
			result[i]=add(result[i], item[i]);		#call add recursively if still not scalars
	return result

def mult(*items):
	#multiply list objects containing lists of lists and numbers. arrays must be same size or scalar
	#same as add but tot=1 and multiply scalars
	allscalars=1; somescalars=0; listsize=1; newitems=[];
	for item in items:
		newitems+=[item]				#add item to newitems list
		if isinstance(item,(int, float)):		#numerical objects
			somescalars=1;
		else:
			if len(item)==1:
				newitems[-1]=item[0];		#convert single element list to component object and replace last element in newitems list
				somescalars=1;
			else:
				allscalars=0;			#not all scalars
				if listsize==1:
					listsize=len(item);
				if listsize!=len(item):
					print "=== Inconsistent shape"
					raise
	if allscalars==1:					#all scalars so add
		tot=1;
		for item in newitems:
			tot=tot*item				#add as scalars
		return tot
	if somescalars==1:
		for i in range(len(newitems)):
			try:
				len(newitems[i]);		#will fail if not item with length
			except:
				newitems[i]=[newitems[i]]*listsize;	#pad out scalars to fit lists e.g. 1=>[1,1,1]
	result=(newitems[0])[:];					#remove bracket after bug fix? use [:] to avoid copy by reference
	for i in range(len(result)):
		for item in newitems[1:]:
			result[i]=mult(result[i], item[i]);		#call add recursively if still not scalars
	return result

alias scancn



