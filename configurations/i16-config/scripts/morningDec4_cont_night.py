global lf
lf=open("logfile4Dec2010_uppos.txt","a")


def log(message):
	print message
	lf.write(message+"\n")
	

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
	pos delta delta_ht
	xpsdisable()
	log("Taking image at delta=%f"%delta())
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc 1
	xpsenable()
	inc delta 0.215
	xpsdisable()
	log("Taking image at delta=%f"%delta())
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc 1
	xpsenable()
	inc delta 0.215
	xpsdisable()
	log("Taking image at delta=%f"%delta())
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc 1
	xpsenable()
	pos delta delta_ht


def autoPeak_fast():
	apdPos(1)
	log("Doing th2th scan")
	scancn th2th [0.015 0.03] 41 checkbeam Tc t 1
	go maxpos
	log("Doing eta scan, will go to max")
	scancn eta 0.01 51 Tc checkbeam t 1 
	go maxpos
	apdPos(0)


def apdPos(temp):
	if(temp==1):
		pos tthp tthp.apd
	if (temp==0):
		pos tthp 69.993


def goUp(eta_ht,delta_ht,im_cnt):
	pos tthp tthp.ccd
	for i in range(0,100,1):
		log("Tc = %f K, x20_anout = %f."%(Tc(),x20_anout()))
		if (324 < Tc()) and (Tc() < 334):
			log("Ok, now taking 9 images at this Tc")
			pos eta eta_ht
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.1075
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.1075
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
		log("At end Tc=%f K. On to next temperature..."%Tc())
		x20_anout(0.38+i*0.005)
		if ((i%5) == 0):
			pos w 120	
			#autoPeak_fast()
		else:
			pos w 120

def goDown(eta_ht,delta_ht,im_cnt):
	pos tthp tthp.ccd
	for i in range(0,100,1):
		log("Tc = %f K, x20_anout = %f."%(Tc(),x20_anout()))
		if (324 < Tc()) and (Tc() < 334):
			log("Ok, now taking 9 images at this Tc")
			pos eta eta_ht
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.1075
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.1075
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
		log("At end Tc=%f K. On to next temperature..."%Tc())
		x20_anout(0.485-i*0.005)
		if ((i%5) == 0):
			pos w 120	
			#autoPeak_fast()
		else:
			pos w 120


#th2th_var=autoPeak()
#eta_ht=th2th_var[0]
#delta_ht=th2th_var[1]
eta_ht=35.77
delta_ht=71.86

log("Continuation of cooling curve...")
im_cnt=155
goDown(eta_ht,delta_ht,im_cnt)
lf.close()
#xpsenable()
#log("Now on to heating curve...")
#goUp(eta_ht,delta_ht)
