print "**************************************************"
print "Running the B18 startup script localStation.py..."
print ""

from org.jscience.physics.quantities import Quantity
from org.jscience.physics.units import Unit
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyUnitsScannable

#new
from exafsscripts.exafs import xas_scans
from exafsscripts.exafs.xas_scans import xas, xanes, estimateXas, estimateXanes, qexafs

#old
#from exafsscripts.exafs import exafsScan
#from exafsscripts.exafs.exafsScan import xas, xanes, estimateXas, estimateXanes


from exafsscripts.vortex import vortexConfig
from exafsscripts.vortex.vortexConfig import vortex

from exafsscripts.xspress import xspressConfig
from exafsscripts.xspress.xspressConfig import xspress

alias("xas")
alias("xanes")
alias("estimateXas")
alias("estimateXanes")
alias("vortex")
alias("xspress")
alias("qexafs")

# to act as the energy during dev
print "creating scannable 'test' which will be used to represent energy during commissionning"
print ""

# to delay scan points so they run afer a certain elapsed time
from gdascripts.pd.time_pds import showtimeClass
print ""
print "creating scannable 'showtime' which will delay scan points until a time has been reached during a scan."
print "usage of 'showtime' scan <motor> <start> <stop> <step> showtime 0 <delay between points in s>"
print ""
showtime = showtimeClass("showtime")
showtime.setLevel(4) # so it is operated before anything else in a scan


from gda.jython.commands.ScannableCommands import cv as cvscan
vararg_alias("cvscan")
vararg_alias("cv")

# to setup the vortex for testing:
# xmapMca.setROIs([[700,750]])

# create objects for test cvscan
#print "creating temporary objects for running test qexafs scans"
#from gda.scan import ContinuousScan
#from gda.device.scannable import DummyContinuouslyScannable
#from gda.device.detector import DummyBufferedDetector
#det1 = DummyBufferedDetector()
#det1.setInputNames(["det1"])
#det1.setName("det1")
#scannable1 = DummyContinuouslyScannable();
#scannable1.setName("scannable1");
#scannable1.setInputNames(["scannable1"])
#scannable1.addObserver(det1);

print "Create topup and beamdown monitors to pause and resume scans"
from gda.device.scannable import TopupScannable
topupMonitor = TopupScannable()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(5)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(60)
topupMonitor.setScannableToBeMonitored(topup)
add_default topupMonitor
from gda.device.scannable import BeamMonitorScannableWithResume
beamdown = BeamMonitorScannableWithResume()
beamdown.setName("beamdown")
beamdown.setTimeout(7200)
beamdown.setWaittime(60)
beamdown.configure()
add_default beamdown

print "Create mono motor temperature monitor to pause and resume scans"
from gda.device.scannable import MonoCoolScannable
monoCooler = MonoCoolScannable()
monoCooler.setName("monoCooler")
monoCooler.setMotorTempPV("BL18B-OP-DCM-01:TEMP4")
monoCooler.setCoolingTimeout(1800)
monoCooler.setTemperatureLimit(125)
monoCooler.setTemperatureCoolLevel(100)
monoCooler.configure()
#add_default monoCooler

from java import util

print "localStation.py completed."
print "**************************************************"
 
