#localStation.py
#For beamline specific initialisation code.
from i06shared import installation
from gda.device.scannable import DummyScannable
from gda.configuration.properties import LocalProperties
print
print "*"*80
print "Performing Beamline I06-shared initialisation code (localStation.py).";
print

print "-----------------------------------------------------------------------------------------------------------------"
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Load utilities: caget(pv), caput(pv,value), attributes(object), "
print "    iterableprint(iterable), listprint(list), frange(start,end,step)"
from gdascripts.utils import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load common physical constants"
from gdascripts.constants import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load nexus metadata commands"
from gdascripts.metadata.nexus_metadata_class import meta   # @UnusedImport
print

ds=DummyScannable('ds')
from i06shared.commands.dirFileCommands import pwd, lwf,nwf,nfn,setSubdirectory,getSubdirectory  # @UnusedImport
from i06shared.commands.switchDataWriter import asciiformat, nexusformat,whichformat  # @UnusedImport
from i06shared.commands.snapshot import snap  # @UnusedImport
from i06shared.functions.aliasFunctions import setAlias, setGdaAlias  # @UnusedImport
from i06shared.constant import *  # @UnusedWildImport
from Diamond.Utility.Functions import logger, getScanNumber,incScanNumber,interruptable,removeDevices,getDevice,isDefaultDevice,removeDefaults,backupDefaults,restoreDefaults  # @UnusedImport
from Diamond.Utility.setTimers import stopwatch,timekeeper,clock,lineTime,pointTime,waitTimer,timer,scanTimer,Timers,Dummies,dummyCounter  # @UnusedImport
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;  # @UnusedImport
from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass;  # @UnusedImport
import __main__  # @UnresolvedImport

beamline = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)

if installation.isLive() and beamline != "lab44":
    from i06shared.devices.Scaler8512 import ca11s,ca12s,ca13s,ca14s,ca21s,ca22s,ca23s,ca24s,ca31s,ca32s,ca33s,ca34s,ca41s,ca42s,ca43s,ca44s,ca11sr,ca12sr,ca13sr,ca14sr,ca21sr,ca22sr,ca23sr,ca24sr,ca31sr,ca32sr,ca33sr,ca34sr,ca41sr,ca42sr,ca43sr,ca44sr,scalar1raw,scaler1  # @UnusedImport
    from i06shared.devices.ADC1Counters import *  # @UnusedWildImport
    from i06shared.devices.ADC2Counters import *  # @UnusedWildImport
    from i06shared.devices.ADC3Counters import *  # @UnusedWildImport
    from i06shared.devices.usePGM import *  # @UnusedImport @UnusedWildImport
    from i06shared.devices.useID import *  # @UnusedImport @UnusedWildImport
    from i06shared.lasers.useSlap1 import laser1, laser1phase,laser1delay,laser1locking  # @UnusedImport
    from i06shared.lasers.useSlap2 import laser2, laser2phase,laser2delay,laser2locking  # @UnusedImport

    CC1temp=DisplayEpicsPVClass('CC1temp','SV06I-BM-CC-01:TEMP','C','%f')
    CC3temp=DisplayEpicsPVClass('CC3temp','SV06I-BM-CC-03:TEMP','C','%f')
    CC4temp=DisplayEpicsPVClass('CC4temp','SV06I-BM-CC-04:TEMP','C','%f')
    CIAtemp=DisplayEpicsPVClass('CIAtemp','SV06I-BM-CIA-01:TEMP','C','%f')
    EC1temp=DisplayEpicsPVClass('EC1temp','SV06I-BM-EC-01:TEMP','C','%f')
    #EC2temp=DisplayEpicsPVClass('EC2temp','SV06I-BM-EC-02:TEMP','C','%f')
    #EC3temp=DisplayEpicsPVClass('EC3temp','SV06I-BM-EC-03:TEMP','C','%f')
    OH1temp=DisplayEpicsPVClass('OH1temp','SV06I-BM-OH-01:TEMP','C','%f')
    M1temp1=DisplayEpicsPVClass('M1temp1','BL06I-OP-COLM-01:TEMP1','C','%f')
    M2temp1=DisplayEpicsPVClass('M2temp1','BL06I-OP-COLM-01:TEMP2','C','%f')
    
from i06shared.devices.setCASum import ca11sum,ca12sum,ca13sum,ca14sum,ca21sum,ca22sum,ca23sum,ca24sum,ca31sum,ca32sum,ca33sum,ca34sum,ca41sum,ca42sum,ca43sum,ca44sum  # @UnusedImport
from i06shared.scan.setSpecialScans import mrscan  # @UnusedImport

from i06shared.devices.usePGM import grating  # @UnusedImport
from i06shared.metadata.setSrsDataFileHeader import fileHeader  # @UnusedImport

#Group the hexapod legs into list
m1legs = [__main__.m1leg1, __main__.m1leg2, __main__.m1leg3,__main__.m1leg4, __main__.m1leg5, __main__.m1leg6];  # @UndefinedVariable
m6legs = [__main__.m6leg1, __main__.m6leg2, __main__.m6leg3, __main__.m6leg4, __main__.m6leg5, __main__.m6leg6];  # @UndefinedVariable

from i06shared.scannables.mode_polarisation_energy_instances import *  # @UnusedWildImport

from i06shared.scan.miscan import miscan  # @UnusedImport

#add checkbeam scannable
from i06shared.scannables.checkbeanscannables import checkrc, checktopup_time, checkfe, checkbeam  # @UnusedImport

#Metadata objects
from i06shared.scannables.stokesParameters import StokesParameters
stokes_parameters = StokesParameters('stokes_parameters', __main__.pol, __main__.laa)
from i06shared.metadata.gapScannable import GapScannable
gap = GapScannable("gap", __main__.smode, __main__.iddgap, __main__.idugap, "mm", "%.3f")  # @UndefinedVariable
from i06shared.metadata.taperScannable import TaperScannable
taper = TaperScannable("taper", __main__.smode, "urad", "%.3f", iddtaper=None, idutaper=None)
from i06shared.metadata.harmonicScannable import HarmonicScannable
harmonic = HarmonicScannable("harmonic", __main__.pol)

print "*"*80; 
print "I06 shared localStation.py completed successfully!"
print;print

