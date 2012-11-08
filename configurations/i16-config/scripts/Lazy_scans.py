def takePic():
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1 
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1 
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1 
def apdPos(temp):
	if(temp==1):
		pos tthp tthp.apd
	if (temp==0):
		pos tthp 69.993

def autoPeak():
	apdPos(1)
	scancn eta 0.01 51 Tc t 1
	go maxpos
	scancn chi 0.01 51 Tc t 1
	go maxpos
	scancn sz 0.1 51 Tc t 1
	scancn th2th [0.01 0.02] 81 Tc t 1
	go maxpos
	apdPos(0)