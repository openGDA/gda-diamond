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

from exafsscripts.exafs import xas_scans
from exafsscripts.exafs.xas_scans import estimateXas, estimateXanes

from exafsscripts.vortex import vortexConfig
from exafsscripts.vortex.vortexConfig import vortex

from exafsscripts.xspress import xspressConfig
from exafsscripts.xspress.xspressConfig import xspress

from exafsscripts.exafs.i20DetectorPreparer import I20DetectorPreparer
from exafsscripts.exafs.i20SamplePreparer import I20SamplePreparer
from exafsscripts.exafs.i20OutputPreparer import I20OutputPreparer
from exafsscripts.exafs.i20ScanScripts import I20XasScan
from exafsscripts.exafs.i20ScanScripts import I20XesScan

loggingcontroller = Finder.getInstance().find("XASLoggingScriptController")

detectorPreparer = I20DetectorPreparer(xspress2system, loggingcontroller)
samplePreparer = I20SamplePreparer()
outputPreparer = I20OutputPreparer()

# switch the commenting on these lines to move to the new scripts which include looping
#from exafsscripts.exafs.xas_scans import xas, xanes, xes
xas = I20XasScan(loggingcontroller,detectorPreparer, samplePreparer, outputPreparer,None)
xes = I20XesScan(loggingcontroller,detectorPreparer, samplePreparer, outputPreparer,None)
xanes = xas

alias("xas")
alias("xanes")
alias("xes")
alias("estimateXas")
alias("estimateXanes")
alias("vortex")
alias("xspress")

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
    if (machineMode() == "User"):
        add_default([topupChecker])
        add_default([absorberChecker])
    else:
        remove_default([topupChecker])
        remove_default([absorberChecker])
else:
    LocalProperties.set("gda.data.scan.datawriter.dataFormat","XasAsciiDataWriter")
    remove_default([topupChecker])
    remove_default([absorberChecker])
    

#
# XES offsets section
#
from xes import calcExpectedPositions, offsetsStore, setOffsets
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
    + "\n"
    
print "****GDA startup script complete.****\n\n"
