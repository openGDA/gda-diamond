setTitle("BSA 10.0mg/ml 100ul injection .0.1ml/min flow rate ")

trig = 10.0 ; # %
print "script running"
diodeReading = d10d2.getPosition()

while d10d2.getPosition() < (diodeReading * ( 1.0 + trig/100.0) ) :
	sleep(0.1)
print "Pilatus will collect now  frames ..."
scan showtime 0 1800 1 ncddetectors d10d2
print "all done" 