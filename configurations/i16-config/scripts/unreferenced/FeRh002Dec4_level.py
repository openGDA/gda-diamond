global lf
lf=open("logfile5Dec2010_cooling02.txt","a")


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
	#xpsdisable()
	log("Taking image at delta=%f"%delta())
	pos x2 1
	pos w 1
	pos x2 0
	pos w 12
	#xpsenable()
	pos w 3
	inc delta 0.23
	#xpsdisable()
	log("Taking image at delta=%f"%delta())
	pos x2 1
	pos w 1
	pos x2 0
	pos w 12
	#xpsenable()
	pos w 3
	inc delta 0.23
	#xpsdisable()
	log("Taking image at delta=%f"%delta())
	pos x2 1
	pos w 1
	pos x2 0
	pos w 12
	#xpsenable()
	pos w 3
	pos delta delta_ht


def autoPeak_fast():
	apdPos(1)
	log("Doing th2th scan")
	scancn th2th [0.015 0.03] 81 checkbeam Tc t 0.1
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
		if (326 < Tc()) and (Tc() < 340):
			log("Ok, now taking 9 images at this Tc")
			pos eta eta_ht
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.12
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.12
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
		log("At end Tc=%f K. On to next temperature..."%Tc())
		x20_anout(0.655+i*0.005)
		if ((i%2) == 0):
			log("Now doing th2th scan.")
			pos eta eta_ht	
			pos delta delta_ht
			autoPeak_fast()
		else:
			pos w 120
		if (Tc() > 340):
			log("Now stopping loop because Tc > 340 K. x20_anout =%f"%x20_anout())
			break
		if (im_cnt > 300):
			break


def goDown(eta_ht,delta_ht,im_cnt):
	pos tthp tthp.ccd
	for i in range(0,100,1):
		log("Tc = %f K, x20_anout = %f."%(Tc(),x20_anout()))
		if (322 < Tc()) and (Tc() < 334):
			log("Ok, now taking 9 images at this Tc")
			pos eta eta_ht
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.12
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
			inc eta 0.12
			takePic(delta_ht)
			im_cnt+=3
			log("#image count: %i"%im_cnt)
			log("last three at eta=%f"%eta())
		log("At end Tc=%f K. On to next temperature..."%Tc())
		x20_anout(0.57-i*0.005)
		if ((i%2) == 0):
			log("Now doing th2th scan.")
			pos eta eta_ht	
			pos delta delta_ht
			autoPeak_fast()
		else:
			pos w 120
		if im_cnt>300:
			log("Image buffer full. Start new file! Breaking this loop now...")
			break

def stayLevel(eta_ht,delta_ht,im_cnt):
	pos tthp tthp.ccd
	for i in range(0,100,1):
		#x20_anout(0.52)
		log("Tc = %f K, x20_anout = %f."%(Tc(),x20_anout()))
		log(ctime())
		log("Ok, now taking 9 images at this Tc")
		pos eta eta_ht
		takePic(delta_ht)
		im_cnt+=3
		log("#image count: %i"%im_cnt)
		log("last three at eta=%f"%eta())
		inc eta 0.075
		takePic(delta_ht)
		im_cnt+=3
		log("#image count: %i"%im_cnt)
		log("last three at eta=%f"%eta())
		inc eta 0.075
		takePic(delta_ht)
		im_cnt+=3
		log("#image count: %i"%im_cnt)
		log("last three at eta=%f"%eta())
		log(ctime())
		log("At end Tc=%f K. On to next measurement..."%Tc())
		if ((i%2) == 0):
			log("Now doing th2th scan.")
			pos eta eta_ht	
			pos delta delta_ht
			pos x6ygap 0.5
			autoPeak_fast()
			pos x6ygap 5
		pos w 300
		if im_cnt>300:
			log("Image buffer full. Start new file! Breaking this loop now...")
			break




#th2th_var=autoPeak()
#eta_ht=th2th_var[0]
#delta_ht=th2th_var[1]
#xpsenable()
#pos w 5
eta_ht=35.7876
delta_ht=71.9023+0.1
pos tthp tthp.ccd
log("Now image file is: FeRh002_6Dec2010_cooling02")
log("First scan no : 169292.dat")
log("starting at "+ctime())
log("Waiting for beam to come on...")
checkbeam
log("Beam now back")
im_cnt=1
#goUp(eta_ht,delta_ht,im_cnt)
goDown(eta_ht,delta_ht,im_cnt)
#stayLevel(eta_ht,delta_ht,im_cnt)
lf.close()
#xpsenable()
#log("Now on to heating curve...")
#goUp(eta_ht,delta_ht)
