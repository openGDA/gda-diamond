symboldic={}

symboldic['P'] = lambda hval,kval,lval: True
symboldic['I'] = lambda hval,kval,lval: (hval+kval+lval)%2 == 0
symboldic['F'] = lambda hval,kval,lval: (hval%2 == 0 and kval%2 == 0 and lval%2 == 0) or (hval%2 == 1 and kval%2 == 1 and lval%2 == 1)
symboldic['A'] = lambda hval,kval,lval: (kval+lval)%2 == 0
symboldic['B'] = lambda hval,kval,lval: (hval+lval)%2 == 0
symboldic['C'] = lambda hval,kval,lval: (hval+kval)%2 == 0
symboldic['R'] = lambda hval,kval,lval: (-hval+kval+lval)%3 == 0
symboldic['.'] = lambda hval,kval,lval: True
symboldic['4'] = lambda hval,kval,lval: True
symboldic['3'] = lambda hval,kval,lval: True
symboldic['2'] = lambda hval,kval,lval: True
symboldic['m'] = lambda hval,kval,lval: True
nonsym=symboldic.keys()
symboldic['tetragonal-41-p1']=lambda hval,kval,lval:  hval !=0 or kval != 0 or (lval)%4 == 0
symboldic['tetragonal-42-p1']=lambda hval,kval,lval:  hval !=0 or kval != 0 or (lval)%2 == 0#
symboldic['tetragonal-43-p1']=lambda hval,kval,lval:  hval !=0 or kval != 0 or (lval)%4 == 0
symboldic['tetragonal-21-p2']=lambda hval,kval,lval: ( (hval== 0 and lval==0) and (kval)%2 == 0 ) or ( (kval==0 and lval== 0) and (hval)%2 == 0 ) or  lval!= 0 or hval*kval != 0 
symboldic['tetragonal-n-p1']=lambda hval,kval,lval: hval*kval*lval != 0 or lval !=0 or ((kval+hval)%2 == 0 and lval==0)  
symboldic['tetragonal-c-p3']=lambda hval,kval,lval: (hval != kval) or ((kval==hval) and lval%2 == 0) 
symboldic['tetragonal-b-p2']=lambda hval,kval,lval: hval*kval*lval != 0 or hval*kval !=0 or  (hval*kval ==0 and (hval%2 ==0 and kval%2 ==0))
symboldic['tetragonal-c-p2']=lambda hval,kval,lval: hval*kval*lval != 0 or hval*kval !=0 or  (hval*kval ==0 and lval%2 ==0)
symboldic['tetragonal-n-p2']=lambda hval,kval,lval: hval*kval*lval != 0 or hval*kval !=0 or  (hval*kval ==0 and ( (hval==0 and (kval+lval)%2 ==0) or (kval ==0  and (hval+lval)%2 ==0) ))


symboldic['monoclinic-21-p1']=lambda hval,kval,lval:  hval !=0 or lval != 0 or (kval)%2 == 0
symboldic['monoclinic-a-p1']=lambda hval,kval,lval:  kval !=0 or (hval)%2 == 0
symboldic['monoclinic-c-p1']=lambda hval,kval,lval:  kval !=0 or (lval)%2 == 0
symboldic['monoclinic-n-p1']=lambda hval,kval,lval:  kval !=0 or (hval+lval)%2 == 0

symboldic['orthorombic-21-p3']=lambda hval,kval,lval:  hval !=0 or kval != 0 or (lval)%2 == 0
symboldic['orthorombic-21-p2']=lambda hval,kval,lval:  hval !=0 or (kval)%2 == 0 or (lval) != 0
symboldic['orthorombic-21-p1']=lambda hval,kval,lval:  hval%2 ==0 or kval != 0 or (lval) != 0

symboldic['orthorombic-a-p3']=lambda hval,kval,lval:  hval%2 ==0 or (lval) != 0
symboldic['orthorombic-b-p3']=lambda hval,kval,lval:  kval%2 == 0 or (lval) != 0
symboldic['orthorombic-n-p3']=lambda hval,kval,lval:  (hval+kval)%2 ==0 or lval !=0 

symboldic['orthorombic-a-p2']=lambda hval,kval,lval:  hval%2 ==0 or (kval) != 0
symboldic['orthorombic-c-p2']=lambda hval,kval,lval:  lval%2 ==0 or (kval) != 0
symboldic['orthorombic-n-p2']=lambda hval,kval,lval:  (hval+lval)%2 ==0 or (kval) != 0

symboldic['orthorombic-b-p1']=lambda hval,kval,lval:  kval%2 ==0 or (hval) != 0
symboldic['orthorombic-c-p1']=lambda hval,kval,lval:  lval%2 ==0 or (hval) != 0
symboldic['orthorombic-n-p1']=lambda hval,kval,lval:  (kval+lval)%2 ==0 or (hval) != 0


def SGinterpreter(sgsymbol='I 4 m m'):
	"""Please enter the space group symbol separated by spaces or commas, 
	monoclinic seeting the unique axis is interpreted as b, it returns the l
	ist of the symbols and the crystal class """
	listsymbol=sgsymbol.split()
	lenlist=len(listsymbol)
	while lenlist < 4:
		listsymbol.append('.')
		lenlist=len(listsymbol) 
#	print listsymbol
	if listsymbol[1] is ('1' or '-1'):
		print "triclinic"
		crystalclass='triclinic'
	elif listsymbol[0].__contains__('R') and listsymbol[1].__contains__('3'):
		print "rhombohedral, using obverse"
		crystalclass=='rombohedral'
	elif (listsymbol[0].__contains__('R') or listsymbol[0].__contains__('P')) and listsymbol[1].__contains__('6'):
		crystalclass=='hexagonal'
	elif listsymbol[1].__contains__('4') is False and listsymbol[2].__contains__('.'):
		print "monoclinic, b axis unique"
		crystalclass='monoclinic'
	elif listsymbol[1].__contains__('4') is False and listsymbol[2].__contains__('3') is False and listsymbol[3].__contains__('.') is False:
		crystalclass='orthorombic'
	elif listsymbol[1].__contains__('4') and listsymbol[2].__contains__('3') is False:
		crystalclass='tetragonal'
	elif listsymbol[2].__contains__('3'):
		crystalclass='cubic'
	return listsymbol,crystalclass
	

def elementinterpreter(listsymbol, crystalclass,nonsym=nonsym):
	"""uses the output of SGinterpreter passed as first and seconf argument to generate the
	diffractionsymbol, that will be used as input in allowed. The default  argument is a dictionary containing the 
	extintion rules associated with the various symbols"""
	poscount=-1
	listinterpretedsymbol=[]
	for element in listsymbol:
		poscount+=1
#		print nonsym
		if nonsym.__contains__(element):			
			listinterpretedsymbol.append(element)
		else:
			interpreted=element.split('/')
			if interpreted[0]==element:
				if nonsym.__contains__(element):			
					listinterpretedsymbol.append(element)
				else:
					listinterpretedsymbol.append(crystalclass+'-'+element+'-p'+str(poscount))
			else:
				for symbol in interpreted:
					if nonsym.__contains__(symbol):			
						listinterpretedsymbol.append(symbol)
					else:
						listinterpretedsymbol.append(crystalclass+'-'+symbol+'-p'+str(poscount))
	return  listinterpretedsymbol


def allowed(hval,kval,lval,listsymbol,symboldic=symboldic, helpon=True):
	helpme="""Warning the extinction rules are implemented fully only for symmorphic space groups, \n only some non symmorphic elements are present.
	Please add them if needed to the dictionary symboldic \n eg symboldic['tetragonal-41-p1']=lambda hval,kval,lval: (lval)%4 == 0	
	The access key is constructed at crystalclass-symbol-position (1,2,3)
	e.g. Bb2b will have orthorombic-b-p1 and orthorombic-b-p3 
	to switch off this printing, please call allowed with helpme=False"""
	if helpon:
		print helpme  
	logical= True
	for element in listsymbol:
		try:
			if symboldic[element](hval,kval,lval) is not True:
				logical =False
		except:
			print "Symmetry element ", 
			print element,
			print "not known"
			print "Please add it to the dictionary" 
			logical= True
	return logical
		


print  "EXAMPLE OF USE"\n
xxx,cc=SGinterpreter('P 21/n 21/n 21/n');

lista=elementinterpreter(xxx,cc)
for hval in range(-3,3):
	for kval in range(-3,3):
		for lval in range(-3,3):
				if allowed(hval,kval,lval,lista,helpon=False) is False:
					print hval,kval,lval, allowed(hval,kval,lval,lista,helpon=False), '\t',

