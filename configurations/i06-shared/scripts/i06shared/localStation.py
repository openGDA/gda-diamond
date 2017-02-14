#localStation.py
#For beamline specific initialisation code.

print "===================================================================";
print "Performing Beamline I06-shared initialisation code (localStation.py).";
print

from i06shared.commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
from i06shared.functions.aliasFunctions import setAlias, setGdaAlias  # @UnusedImport
from i06shared.constant import *  # @UnusedWildImport
from Diamond.Utility.Functions import logger, getScanNumber,incScanNumber,interruptable,removeDevices,getDevice,isDefaultDevice,removeDefaults,backupDefaults,restoreDefaults  # @UnusedImport
from Diamond.Utility.setTimers import stopwatch,timekeeper,clock,lineTime,pointTime,waitTimer,timer,scanTimer,Timers,Dummies,dummyCounter  # @UnusedImport
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;  # @UnusedImport
from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass;  # @UnusedImport

try:
	#Set up the Diamond NumPy
	print "-------------------------------------------------------------------"
	print "Note: Use dnp (Diamond NumPy) from scisoftpy for data handling and plotting in GDA"
	print "Note: Use help dnp for all commands"
	print "Note: Use help <component> for help on all components ..." 
	print "      (dnp.core, dnp.io, dnp.maths, dnp.plot, dnp.image)"
	print "For example: "
	print "		 To load data:  data=dnp.io.load(/full/path/to/data/file, formats=['srs'], asdict=True)"
	print "		 To plot data:  dnp.plot.line(x, y)"
	print "		 To plot image: dnp.plot.image(data)"
	import scisoftpy as dnp;  # @UnusedImport
except:
	import sys
	exceptionType, exception, traceback1=sys.exc_info();
	print "Error:  import scisoftpy raise exceptions"
	logger.dump("---> ", exceptionType, exception, traceback1)

from i06shared.devices.setCASum import ca11sum,ca12sum,ca13sum,ca14sum,ca21sum,ca22sum,ca23sum,ca24sum,ca31sum,ca32sum,ca33sum,ca34sum,ca41sum,ca42sum,ca43sum,ca44sum  # @UnusedImport
from i06shared.scan.setSpecialScans import mrscan  # @UnusedImport
from i06shared.scan.fastEnergyScan import zacscan,zacstop,zacmode,fesController,fesData, fastEnergy,uuu,i06util  # @UnusedImport
from i06shared.devices.usePGM import grating  # @UnusedImport
from i06shared.devices.useID import iddpol,denergy,hdenergy,iddrpenergy,idupol,uenergy,huenergy,idurpenergy,duenergy,iddhar,iduhar  # @UnusedImport
from i06shared.setSrsDataFileHeader import fileHeader,blList,idList,pgmList,energyList,slitList,commonMirrorList  # @UnusedImport

print "==================================================================="; print; print;

print "Creating i06ccd2 detector (from end of localStation.py)"
#import scannables.detector.andormcd
#i06ccd2 = scannables.detector.andormcd.AndorMCD('i06ccd2')


