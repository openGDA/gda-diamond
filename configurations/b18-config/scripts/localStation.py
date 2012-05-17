print "**************************************************"
print "Running the B18 startup script localStation.py..."
print ""

from exafsscripts.exafs.xas_scans import estimateXas, estimateXanes
from exafsscripts.vortex.vortexConfig import vortex
from exafsscripts.xspress.xspressConfig import xspress
from exafsscripts.exafs.b18DetectorPreparer import B18DetectorPreparer
from exafsscripts.exafs.b18SamplePreparer import B18SamplePreparer
from exafsscripts.exafs.b18OutputPreparer import B18OutputPreparer
from exafsscripts.exafs.b18ScanScripts import XasScan, QexafsScan
from gda.device.scannable import TopupScannable
from gda.device.scannable import BeamMonitorScannableWithResume
from gda.device.scannable import MonoCoolScannable
from gda.factory import Finder
from gda.configuration.properties import LocalProperties

original_header = Finder.getInstance().find("datawriterconfig").clone().getHeader()[:]

detectorPreparer = B18DetectorPreparer(qexafs_energy, mythen, ionc_stanfords, ionc_gas_injectors)
samplePreparer = B18SamplePreparer(sam1, sam2, cryo, lakeshore, eurotherm, pulsetube, samplewheel, userstage)
outputPreparer = B18OutputPreparer()
xas = XasScan(detectorPreparer, samplePreparer, outputPreparer)
qexafs = QexafsScan(detectorPreparer, samplePreparer, outputPreparer, qexafs_energy, qexafs_counterTimer01)
xanes = xas

alias("xas")
alias("xanes")
alias("estimateXas")
alias("estimateXanes")
alias("vortex")
alias("xspress")
alias("qexafs")

from gda.jython.commands.ScannableCommands import cv as cvscan
vararg_alias("cvscan")
vararg_alias("cv")

print "Create topup, beam and mono motor temperature monitors to pause and resume scans"
topupMonitor = TopupScannable()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(5)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(60)
topupMonitor.setScannableToBeMonitored(topup)

if (LocalProperties.get("gda.mode") == 'live'):
    add_default topupMonitor

beamMonitor = BeamMonitorScannableWithResume()
beamMonitor.setName("beamMonitor")
beamMonitor.setTimeout(7200)
beamMonitor.setWaittime(60)
beamMonitor.configure()
if (LocalProperties.get("gda.mode") == 'live'):
    add_default beamMonitor

monoCooler = MonoCoolScannable()
monoCooler.setName("monoCooler")
monoCooler.setMotorTempPV("BL18B-OP-DCM-01:TEMP4")
monoCooler.setCoolingTimeout(1800)
monoCooler.setTemperatureLimit(125)
monoCooler.setTemperatureCoolLevel(100)
monoCooler.configure()

from gdascripts.pd.time_pds import showtimeClass
showtime = showtimeClass("showtime")
showtime.setLevel(4) # so it is operated before anything else in a scan

original_header = Finder.getInstance().find("datawriterconfig").clone().getHeader()[:]

print "localStation.py completed."
print "**************************************************"
