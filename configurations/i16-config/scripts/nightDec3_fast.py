def autoPeak():
	apdPos(1)
	scancn eta 0.01 51 Tc checkbeam t 1 
	go maxpos
	scancn sz 0.1 51 checkbeam Tc t 1 
	go maxpos
	scancn th2th [0.015 0.03] 51 checkbeam Tc t 1
	go maxpos
	apdPos(0)

def takePic():
	#xpsenable()
	pos delta 72.045
	inc delta 0.215
	#xpsdisable()
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	#xpsenable()
	inc delta -0.215
	#xpsdisable() 
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	#xpsenable()
	inc delta -0.215
	#xpsdisable() 
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	#xpsenable()
	pos delta 72.045

def autoPeak_fast():
	apdPos(1)
	scancn th2th [0.015 0.03] 41 checkbeam Tc t 1
	go maxpos
	scancn eta 0.01 51 Tc checkbeam t 1 
	go maxpos
	apdPos(0)


def apdPos(temp):
	if(temp==1):
		pos tthp tthp.apd
	if (temp==0):
		pos tthp 69.993

def goUp():
	pos tthp tthp.ccd
	for i in range(0,100,1):
		inc eta 0.1075
		takePic()
		inc eta -0.1075
		takePic()
		inc eta -0.1075
		takePic()
		inc eta 0.1075
		x20_anout(0.38+i*0.005)
		if ((i%5) == 0):
			xpsenable()	
			autoPeak_fast()
		else:
			pos w 120

def goDown():
	pos tthp tthp.ccd
	for i in range(0,100,1):
		inc eta 0.1075
		takePic()
		inc eta -0.1075
		takePic()
		inc eta -0.1075
		takePic()
		inc eta 0.1075
		x20_anout(0.88-i*0.005)
		if ((i%5) == 0):
			xpsenable()	
			autoPeak_fast()
		else:
			pos w 120

