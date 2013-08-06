print "Initialization Started";

from exafsscripts.exafs.b18DetectorPreparer import B18DetectorPreparer
from exafsscripts.exafs.b18SamplePreparer import B18SamplePreparer
from exafsscripts.exafs.b18OutputPreparer import B18OutputPreparer
from exafsscripts.exafs.xas_scan import XasScan
from exafsscripts.exafs.qexafs_scan import QexafsScan
from gda.device.scannable import TopupScannable
from gda.device.scannable import BeamMonitorScannableWithResume
from gda.device.scannable import MonoCoolScannable
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.jython.scriptcontroller.logging import LoggingScriptController
from gda.jython.scriptcontroller.logging import XasLoggingMessage
from gda.device.monitor import EpicsMonitor
from gda.data.scan.datawriter import NexusExtraMetadataDataWriter

XASLoggingScriptController = Finder.getInstance().find("XASLoggingScriptController")
commandQueueProcessor = Finder.getInstance().find("commandQueueProcessor")
ExafsScriptObserver = Finder.getInstance().find("ExafsScriptObserver")
datawriterconfig = Finder.getInstance().find("datawriterconfig")

original_header = Finder.getInstance().find("datawriterconfig").clone().getHeader()[:]

NexusExtraMetadataDataWriter.removeAllMetadataEntries()

if (LocalProperties.get("gda.mode") == 'live'):
    detectorPreparer = B18DetectorPreparer(qexafs_energy, mythen, ionc_stanfords, ionc_gas_injectors.getGroupMembers())
else:
    detectorPreparer = B18DetectorPreparer(qexafs_energy, None, ionc_stanfords, ionc_gas_injectors.getGroupMembers())
samplePreparer = B18SamplePreparer(sam1, sam2, cryo, lakeshore, eurotherm, pulsetube, samplewheel, userstage)
outputPreparer = B18OutputPreparer(datawriterconfig)

xas = XasScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, energy, counterTimer01)
qexafs = QexafsScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, qexafs_energy, qexafs_counterTimer01)
xanes = xas

alias("xas")
alias("xanes")
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

beamMonitor = BeamMonitorScannableWithResume()
beamMonitor.setName("beamMonitor")
beamMonitor.setTimeout(7200)
beamMonitor.setWaittime(60)
beamMonitor.configure()

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

if (LocalProperties.get("gda.mode") == 'live'):
    sample_temperature = EpicsMonitor()
    sample_temperature.setName("sample_temperature")
    sample_temperature.setExtraNames(["sample_temperature"])
    sample_temperature.setPvName("ME08G-EA-GIR-01:TEMP1")
    blower_temperature = EpicsMonitor()
    blower_temperature.setName("blower_temperature")
    blower_temperature.setExtraNames(["blower_temperature"])
    blower_temperature.setPvName("ME08G-EA-GIR-01:TCTRL1:PV:RBV")
    add_default topupMonitor
    add_default beamMonitor

print "Initialization Complete";