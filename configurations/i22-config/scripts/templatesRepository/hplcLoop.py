setTitle("Lysozyme Conc test samples 0.2ml/min flow rate 1s exposure")

#trig = 10.0 ; # %
print "script running"
diodeReading = d10d2.getPosition()

pos shutter "Open"

n = 0

while n < 6:
	if d10d2.getPosition() < 0.025:
		sleep(0.1)
	else:
		print "Pilatus will collect now  frames ..."
		#scan showtime 0 10 1 ncddetectors d10d2
		staticscan ncddetectors
		n = n + 1 

pos shutter "Close"

print "all done" 
