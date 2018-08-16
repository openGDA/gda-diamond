def takePic():
	#take pictures in 3 different Q position 10 sec count time 
	#with two picture per position
	
	#centre of the peak
	pos delta 72.027
	pos eta 36.1308
	pos w 3
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1

	inc delta -0.4
	inc eta -0.2
	pos w 3
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1


	inc delta 0.8
	inc eta 0.4
	pos w 3
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1
	pos x2 1
	pos w 1
	pos x2 0
	scan dummy 0 15 1 Tc t 1

while(1):#infinate loop to keep taking pictures until the end of time.
	takePic()