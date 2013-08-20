import sys
from time import sleep

from gdascripts.messages import handle_messages;
from Diamond.PseudoDevices.FastEnergyScan import FastEnergyScanControlClass, FastEnergyScanIDModeClass;
from Diamond.PseudoDevices.FastEnergyScan import FastEnergyDeviceClass;
from Diamond.PseudoDevices.FastEnergyScan import EpicsScandataDeviceClass;
from Diamond.PseudoDevices.FastEnergyScan import EpicsWaveformDeviceClass;

from gda.scan import PointsScan;

def update(controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False):
	handle_messages.log(controller, msg, exceptionType, exception, traceback, Raise)

#exec("[fesController, sdd, fesStopper, fastEnergy] = [1,1,1,1]");

rootPV = "BL06I-MO-FSCAN-01";
fesController = FastEnergyScanControlClass("fesController", rootPV);
zacmode = FastEnergyScanIDModeClass("zacmode", fesController);
#fesData = EpicsScandataDeviceClass("fesData", rootPV);
fesData = EpicsWaveformDeviceClass("fesData", rootPV, 6);
fastEnergy = FastEnergyDeviceClass("fastEnergy", fesController, fesData);

#Do not change mode on startup
#fesController.setIDMode(1);

	
#A function to run the I06 energy constant velocity scan by using the  FastEnergyScanClass class
def cvscan(startEnergy, endEnergy, scanTime, pointTime):
	fesData.reset();
	fesController.setEnergyRange(startEnergy, endEnergy);
	fesController.setTime(scanTime, pointTime);
	fesController.setIDMode(1);

	if pointTime > 2.0:
		fastEnergy.setDelay(pointTime/2.0);
	elif pointTime>0.5:
		fastEnergy.setDelay(pointTime/5.0);
	else:
		fastEnergy.setDelay(pointTime/10.0);
		
	numPoint = fesController.getNumberOfPoint();
	step=1.0*(endEnergy - startEnergy)/numPoint;
	
#	scan timer 0 scanTime pointTime fastEnergy 1 sdd 10
#	pscan fastEnergy 0 1 numPoint fesData 0 1;
	pscan([fastEnergy,0,1,numPoint,fesData,0,1]);

def fastscan(startEnergy, endEnergy, scanTime, pointTime):
	return cvscan(startEnergy, endEnergy, scanTime, pointTime);

def fescan(startEnergy, endEnergy, scanTime, pointTime):
	return cvscan(startEnergy, endEnergy, scanTime, pointTime);

def zacscan(startEnergy, endEnergy, scanTime, pointTime):
	try:
		return fastEnergy.cvscan(startEnergy, endEnergy, scanTime, pointTime);
	except :
		type, exception, traceback = sys.exc_info()
		update(None,"Error in zacscan", type, exception , traceback, False)		

alias("cvscan");
alias("fastscan");
alias("fescan");
alias("zacscan");
	
#	theScan = PointsScan([fastEnergy,0,1,numPoint,fesData,0,1]);
#	theScan.runScan();

	
#	scan fastEnergy 0 numPoint 1 fesData
		


from Diamond.Objects.FastEnergyScan import FastEnergyScanClass
#A function to run the I06 energy constant velocity scan by using the  FastEnergyScanClass class
def cvscan_old(startEnergy, endEnergy,scanTime, pointTime):
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
	
	
