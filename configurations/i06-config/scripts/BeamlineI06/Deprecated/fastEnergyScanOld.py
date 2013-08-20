from time import sleep
from java import lang

#from BeamlineI06.Objects.FastEnergyScan import FastEnergyScanClass
from Diamond.Objects.FastEnergyScan import FastEnergyScanClass

#A function to run the I06 energy constant velocity scan by using the  FastEnergyScanClass class
def cvscan(startEnergy, endEnergy,scanTime, pointTime):
	#to check the FastEnergyScan object exists
	if not 'fescan' in dir():
		fescan = FastEnergyScanClass();

	fescan.atScanStart()
	
	if not fescan.checkMotorReady():
		print "Fast energy scan can not be performed.";
		return;

	#setup scan parameters
	fescan.setEnergyRange(startEnergy, endEnergy);
	fescan.setTime(scanTime, pointTime);
	
	#trigger the scan
	fescan.build()
	print "Start building the scan..."

	while not fescan.isBuilt():
		#print 'Building...'
		sleep(2);

	print "Start scan..."
	fescan.start()
	
	while fescan.isBusy():
		if not fescan.isScanning():
			sleep(3);
		else:
			#sleep(pointTime*10);
			sleep(10);
			fescan.plotData();
	else:
		print "Total points: "  + str(fescan.getDataNumbers());
		print 'Collecting data...'

	fescan.saveData();	
	print 'Data saved in file';
	fescan.atScanEnd()


#lpr -P b.i06.cc1.col.1 -o InputSlot=Auto -o Resolution=600dpi -o PageSize=A4 -o Duplex=DuplexNoTumble
	
	
