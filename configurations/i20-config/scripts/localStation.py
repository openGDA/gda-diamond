print "\n\n****Running the I20 startup script****\n\n"


from org.jscience.physics.quantities import Quantity
from org.jscience.physics.units import Unit
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.jython import JythonServerFacade
from gda.scan import ScanBase

from devices import RealBlades
from devices.RealBlades import BladeAngle
from devices.RealBlades import SubtractAngle
from devices.RealBlades import AverageAngle

from exafsscripts.exafs.i20DetectorPreparer import I20DetectorPreparer
from exafsscripts.exafs.i20SamplePreparer import I20SamplePreparer
from exafsscripts.exafs.i20OutputPreparer import I20OutputPreparer
from exafsscripts.exafs.xas_scan import XasScan
from exafsscripts.exafs.xes_scan import I20XesScan

from time import sleep

ScanBase.interrupted = False
ScriptBase.interrupted = False

XASLoggingScriptController = Finder.getInstance().find("XASLoggingScriptController")
commandQueueProcessor = Finder.getInstance().find("commandQueueProcessor")
ExafsScriptObserver = Finder.getInstance().find("ExafsScriptObserver")
datawriterconfig = Finder.getInstance().find("datawriterconfig")
datawriterconfig_xes = Finder.getInstance().find("datawriterconfig_xes")

sensitivities = [i0_stanford_sensitivity, it_stanford_sensitivity,iref_stanford_sensitivity,i1_stanford_sensitivity]
sensitivity_units = [i0_stanford_sensitivity_units,it_stanford_sensitivity_units,iref_stanford_sensitivity_units,i1_stanford_sensitivity_units]
offsets = [i0_stanford_offset,it_stanford_offset,iref_stanford_offset,i1_stanford_offset]
offset_units = [i0_stanford_offset_units,it_stanford_offset_units,iref_stanford_offset_units,i1_stanford_offset_units]

detectorPreparer = I20DetectorPreparer(xspress2system, XASLoggingScriptController,sensitivities, sensitivity_units ,offsets, offset_units,cryostat,ionchambers,I1,xmapMca,topupChecker)
samplePreparer = I20SamplePreparer()
outputPreparer = I20OutputPreparer(datawriterconfig,datawriterconfig_xes)

xas = XasScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, bragg1, ionchambers, True, True, True)
xes = I20XesScan(XASLoggingScriptController,detectorPreparer, samplePreparer, outputPreparer,commandQueueProcessor, XASLoggingScriptController, ExafsScriptObserver, sample_x, sample_y, sample_z, sample_rot, sample_fine_rot)
xanes = xas

alias("xas")
alias("xanes")
alias("xes")

# To make scans return to the start after being run
# Should be for commissioning only.
scansReturnToOriginalPositions = 1

# to delay scan points so they run afer a certain elapsed time
print "Creating some scannables useful for recording time during scans..."
from gdascripts.pd.time_pds import showtimeClass, waittime
print "Creating scannable 'w' which will delay scan points until a time has been reached during a scan."\
+ "\nusage of 'w':    scan <motor> <start> <stop> <step> w 0 <delay between points in s>\n\n"

w = showtimeClass("w")
w.setLevel(10) # so it is operated before anything else in a scan


# These scannables are checked before any scan data point
# You may comment them out to remove the checking.
if LocalProperties.get("gda.mode") == "live":
    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")
    if (machineMode() == "No Beam"):
        remove_default([topupChecker])
        remove_default([absorberChecker])
        remove_default([shutterChecker])
    else:
        add_default([topupChecker])
        add_default([absorberChecker])
        add_default([shutterChecker])
else:
    #LocalProperties.set("gda.data.scan.datawriter.dataFormat","XasAsciiDataWriter")
    remove_default([topupChecker])
    remove_default([absorberChecker])
    remove_default([shutterChecker])
    

#
# XES offsets section
#
from xes import calcExpectedPositions, offsetsStore, setOffsets
try:
    offsetsStore.reapply()
except:
    pass
from gda.device.scannable import TwoDScanPlotter
twodplotter = TwoDScanPlotter()
twodplotter.setName("twodplotter")
#offsetsStore.apply() # reads the default store from its xml file and applys the GDA-level offsets
#
# to calibrate the XES spectrometer:
# 1. move all motors to the correct position for a known peak visible in the Vortex MCA
# 2. run the following command:
#       calcExpectedPositions.recordFromLive(<the energy of the peak>)
#    This will store the offsets to an xml file and so will be reused when the GDA is restarted.

############### Pseudo Devices for Angle ####################
# Constants
#s1_da = 17.092 #m
#s1_db = 17.812 #m

#s1_xa_o = -0.20
#s1_xb_o = 1.05
#s1_ya_o = -4.50
#s1_yb_o = 3.47

# NOTE: DashboardObserver is used to notify the value changed in the PseudoDevice.
#s1_xa_mrad = BladeAngle("s1_xa_mrad","s1_xa", s1_xa_o, s1_da, "DashboardObserver")
#s1_xb_mrad = BladeAngle("s1_xb_mrad","s1_xb", s1_xb_o, s1_db, "DashboardObserver")
#s1_ya_mrad = BladeAngle("s1_ya_mrad","s1_ya", s1_ya_o, s1_da, "DashboardObserver")
#s1_yb_mrad = BladeAngle("s1_yb_mrad","s1_yb", s1_yb_o, s1_db, "DashboardObserver")

#s1_hgap_mrad    = SubtractAngle("s1_hgap_mrad",   s1_xa_mrad, s1_xb_mrad, "DashboardObserver");
#s1_hoffset_mrad = AverageAngle("s1_hoffset_mrad", s1_xa_mrad, s1_xb_mrad, "DashboardObserver");

#s1_vgap_mrad    = SubtractAngle("s1_vgap_mrad",   s1_ya_mrad, s1_yb_mrad, "DashboardObserver");
#s1_voffset_mrad = AverageAngle("s1_voffset_mrad", s1_ya_mrad, s1_yb_mrad, "DashboardObserver");

#s1_hgap_mrad.setRef(s1_hoffset_mrad)
#s1_hoffset_mrad.setRef(s1_hgap_mrad)

#s1_vgap_mrad.setRef(s1_hoffset_mrad)
#s1_hoffset_mrad.setRef(s1_vgap_mrad)

########################## End ##############################
if LocalProperties.get("gda.mode") == "live":
    # To set up the ADC for use in GDA
    run 'adc_monitor'
    # To make the scannables for controlling the mono crystal piezos through the EPICS closed-loop
    # July2012 do not need this script anymore 
    #run 'crystal_pid'

    run "xspress_config"
    print "\nXspress detector set to high (>8KeV) mode."\
    + "\nIf you wish to collect predominately at lower energies, type:"\
    + "\nswitchXspressToLowEnergyMode()"\
    + "\nto change the Xspress settings. Type:"\
    + "\nswitchXspressToHighEnergyMode()"\
    + "\n to changes the settings back again."\
    + "\n"\
    + "To find out current mode type:\n"\
    + "finder.find(\"DAServer\").getStartupCommands()\n"
    
    FFI0.setInputNames([])
    
    run "vortexLiveTime"
    testVortexWiredCorrectly()
    
    
else :
    # simulation (dummy mode) specific settings
    if material() == None:
        material('Si')
print "****GDA startup script complete.****\n\n"
