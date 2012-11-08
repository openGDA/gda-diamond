def autoPeak():
	apdPos(1)
	scancn eta 0.01 51 Tc t 1 checkbeam
	go maxpos
	scancn chi 0.01 51 Tc t 1 checkbeam
	go maxpos
	scancn sz 0.1 51 Tc t 1 checkbeam
	go maxpos
	scancn th2th [0.015 0.03] 41 Tc t 1 checkbeam
	go maxpos
	apdPos(0)

def apdPos(temp):
	if(temp==1):
		pos tthp tthp.apd
	if (temp==0):
		pos tthp 69.993

def goUpandDown():
	for i in range(0,100,1):
		xpsdisable()
		pos x2 1;pos x2 0
		pos w 2	
		pos x2 1;pos x2 0
		pos w 2
		pos x2 1;pos x2 0
		pos w 2
		xpsenable()
		x20_anout(0.38+i*0.006)
		autoPeak()
	for i in range(0,100,1):
		xpsdisable()
		pos x2 1;pos x2 0
		pos w 2
		pos x2 1;pos x2 0
		pos w 2
		pos x2 1;pos x2 0	
		pos w 2
		xpsenable()
		x20_anout(0.88-i*0.006)
		autoPeak()

