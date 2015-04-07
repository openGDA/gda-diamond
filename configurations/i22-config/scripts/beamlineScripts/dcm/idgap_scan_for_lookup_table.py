print "running the harmonic script"

# set up some things first
import time
import scisoftpy as dnp
from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

for e in dnp.arange(10.0, 21.0, 0.4):
	pos bkeV e
	pos calibrated_perp e
	pos finepitch 0
	pos pitch -75
	setTitle("Pitch scan for bkeV = "+str(e))
	scan finepitch -100 100 0.5 d6d1
	pos finepitch -100
	go maxval
	
	pos idgap_mm 5
	sleep(1)
	setTitle("idgap scan for bkeV = "+str(e))
	scan idgap_mm 5 10 0.005 d6d1
	position = maxval.result.maxpos
	
	# save the data back out
	filenum = i22NumTracker.getCurrentFileNumber()
	file = open(PathConstructor.createFromDefaultProperty()+"harmonic_parameters_"+time.strftime("%Y-%m-%d")+".dat","a")
	file.write("%f, %f , %f , %d \n" % (e, bragg.getPosition() , position, filenum))
	file.close()
	
print "All Done!"