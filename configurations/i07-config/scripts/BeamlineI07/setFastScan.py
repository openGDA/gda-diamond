
import sys;
from time import sleep, ctime;


from Diamond.Scans.FastScan import FastScanControlClass
from Diamond.Scans.FastScan import EpicsMCADataDeviceClass

from Diamond.Scans.FastScan import FastMotionDeviceClass

#exec("[fastController, fastData, fastMotor] = [None, None, None]");

rootPV = "BL07I-EA-DET-01:MCA-01";
numberOfMCA=1;

#exec([fastController, fastData, fastMotion]=[None, None, None]);

fastController = FastScanControlClass("fastController");
fastData = EpicsMCADataDeviceClass("fastData", rootPV, numberOfMCA);


#A function to run the fast scan
def cvscan(scannableDevice, startPosition, stopPosition,scanTime, pointTime):
	fastController.setScannable(scannableDevice);
	fastMotion = FastMotionDeviceClass("fastMotion", fastController, fastData);
		
	fastController.setAcceleration(0.2);
	fastController.setMotorSpeed(6);

	try:
		fastMotion.cvscan(startPosition, stopPosition, scanTime, pointTime);
	except:
		type, exception, traceback = sys.exc_info();
		logger.fullLog(None, "Error in stopping the zacscan ", type, exception , traceback, False);		

alias("cvscan");

#Usage:
#cvscan d4dx -100 -50 50 1
#cvscan omega 0 90 30 0.5
