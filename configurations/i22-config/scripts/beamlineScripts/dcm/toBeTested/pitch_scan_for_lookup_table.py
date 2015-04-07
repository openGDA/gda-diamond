import java
from gda.data import NumTracker
from gda.data import PathConstructor
from gda.analysis.io import NexusLoader
from math import cos
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

results = []

# determines from scan idgap_mm 6 8 0.01 d3diode2 with pos bkeV 7.0
energy_start = 3.71;
energy_end= 20.0

energyPos = energy_start ;

file = open(PathConstructor.createFromDefaultProperty()+"pitch_parameters.csv","a")
file.write("Energy , peak, max, intensity")
file.close()

while energyPos < energy_end:
	pos energy energyPos

	scan pitch -900 -1050 2 d3diode2	
	positionPeak = peak.result.pos
	positionMax = maxval.result.maxpos
	valueMax = maxval.result.maxval
	print str(energyPos) +" , "+str(positionPeak)+" , "+str(positionMax)+" , "+str(valueMax)

	# save the data back out
	file = open(PathConstructor.createFromDefaultProperty()+"pitch_parameters.csv","a")
	file.write("%f , %f\n" % (energyPos,position))
	file.close()
	
	energyPos += 0.5 
