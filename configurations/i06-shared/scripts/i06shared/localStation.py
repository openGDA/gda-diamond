#localStation.py
#For beamline specific initialisation code.
print
print "*"*80
print "Performing Beamline I06-shared initialisation code (localStation.py).";
print

from i06shared.commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
from i06shared.functions.aliasFunctions import setAlias, setGdaAlias  # @UnusedImport
from i06shared.constant import *  # @UnusedWildImport
from Diamond.Utility.Functions import logger, getScanNumber,incScanNumber,interruptable,removeDevices,getDevice,isDefaultDevice,removeDefaults,backupDefaults,restoreDefaults  # @UnusedImport
from Diamond.Utility.setTimers import stopwatch,timekeeper,clock,lineTime,pointTime,waitTimer,timer,scanTimer,Timers,Dummies,dummyCounter  # @UnusedImport
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;  # @UnusedImport
from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass;  # @UnusedImport
import __main__  # @UnresolvedImport

from i06shared.devices.Scaler8512 import ca11s,ca12s,ca13s,ca14s,ca21s,ca22s,ca23s,ca24s,ca31s,ca32s,ca33s,ca34s,ca41s,ca42s,ca43s,ca44s,ca11sr,ca12sr,ca13sr,ca14sr,ca21sr,ca22sr,ca23sr,ca24sr,ca31sr,ca32sr,ca33sr,ca34sr,ca41sr,ca42sr,ca43sr,ca44sr,scalar1raw,scaler1  # @UnusedImport
from i06shared.devices.setCASum import ca11sum,ca12sum,ca13sum,ca14sum,ca21sum,ca22sum,ca23sum,ca24sum,ca31sum,ca32sum,ca33sum,ca34sum,ca41sum,ca42sum,ca43sum,ca44sum  # @UnusedImport
from i06shared.devices.ADC1Counters import *  # @UnusedWildImport
from i06shared.devices.ADC2Counters import *  # @UnusedWildImport
from i06shared.devices.ADC3Counters import *  # @UnusedWildImport
from i06shared.scan.setSpecialScans import mrscan  # @UnusedImport
from i06shared.devices.usePGM import *  # @UnusedImport @UnusedWildImport
from i06shared.devices.useID import *  # @UnusedImport @UnusedWildImport
from i06shared.setSrsDataFileHeader import fileHeader  # @UnusedImport
from i06shared.lasers.useSlap1 import laser1, laser1phase,laser1delay,laser1locking  # @UnusedImport
#Group the hexapod legs into list
m1legs = [__main__.m1leg1, __main__.m1leg2, __main__.m1leg3,__main__.m1leg4, __main__.m1leg5, __main__.m1leg6];  # @UndefinedVariable
m6legs = [__main__.m6leg1, __main__.m6leg2, __main__.m6leg3, __main__.m6leg4, __main__.m6leg5, __main__.m6leg6];  # @UndefinedVariable
from i06shared.scannables.mode_polarisation_energy_instances import *  # @UnusedWildImport
idd,idu,dpu,dmu=SourceMode.SOURCE_MODES
pc,nc,lh,lv,la=Polarisation.POLARISATIONS

print "*"*80; 
print "I06 shared localStation.py completed successfully!"
print;print

