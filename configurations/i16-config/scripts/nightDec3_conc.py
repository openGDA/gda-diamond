def autoPeak():
	apdPos(1)
	scancn eta 0.01 51 Tc checkbeam t 1 
	go maxpos
	scancn chi 0.01 51 checkbeam Tc t 1
	go maxpos
	scancn sz 0.1 51 checkbeam Tc t 1 
	go maxpos
	scancn th2th [0.015 0.03] 51 checkbeam Tc t 1
	go maxpos
	apdPos(0)
	return [eta(),delta()]

def takePic(delta_ht):
	xpsenable()
	pos delta delta_ht
	xpsdisable()
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	xpsenable()
	inc delta 0.215
	xpsdisable() 
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	xpsenable()
	inc delta 0.215
	xpsdisable() 
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	xpsenable()
	pos delta delta_ht

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

def goUp(eta_ht,delta_ht):
	pos tthp tthp.ccd
	for i in range(0,100,1):
		if (328 < Tc()) and (Tc()<336): 
			pos eta eta_ht
			takePic(delta_ht)
			inc eta 0.1075
			takePic(delta_ht)
			inc eta 0.1075
			takePic(delta_ht)
		x20_anout(0.38+i*0.005)
		if ((i%5) == 0):
			xpsenable()	
			autoPeak_fast()
		else:
			pos w 120

def goDown(eta_ht,delta_ht):
	pos tthp tthp.ccd
	for i in range(0,100,1):
		if (324 < Tc()) and (Tc() < 334):
			pos eta eta_ht
			takePic(delta_ht)
			inc eta 0.1075
			takePic(delta_ht)
			inc eta 0.1075
			takePic(delta_ht)
		x20_anout(0.88-i*0.005)
		if ((i%5) == 0):
			xpsenable()	
			autoPeak_fast()
		else:
			pos w 120

xpsenable()
th2th_var=autoPeak()
eta_ht=th2th_var[0]
delta_ht=th2th_var[1]
goDown(eta_ht,delta_ht)
xpsenable()
goUp(eta_ht,delta_ht)