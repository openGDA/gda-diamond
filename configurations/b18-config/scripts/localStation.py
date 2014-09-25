print "Initialization Started";

from uk.ac.gda.server.exafs.scan.preparers import B18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import B18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import B18OutputPreparer
from uk.ac.gda.server.exafs.scan import XasScan
# from exafsscripts.exafs.qexafs_scan import QexafsScan
from gda.device.scannable import TopupChecker
from gda.device.scannable import BeamMonitor
from gda.device.scannable import MonoCoolScannable
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.jython.scriptcontroller.logging import LoggingScriptController
from gda.scan import ScanBase#this is required for skip current repetition to work BLXVIIIB-99
from gda.device.monitor import EpicsMonitor
#from gda.data.scan.datawriter import NexusExtraMetadataDataWriter
from gda.data.scan.datawriter import NexusDataWriter
# from exafsscripts.exafs.config_fluoresence_detectors import XspressConfig, VortexConfig, Xspress3Config
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm, meta_clear_alldynamical

XASLoggingScriptController = Finder.getInstance().find("XASLoggingScriptController")
commandQueueProcessor = Finder.getInstance().find("commandQueueProcessor")
# ExafsScriptObserver = Finder.getInstance().find("ExafsScriptObserver")


datawriterconfig = Finder.getInstance().find("datawriterconfig")
original_header = Finder.getInstance().find("datawriterconfig").getHeader()[:]
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")


# xspressConfig = XspressConfig(xspress2system, ExafsScriptObserver)
# vortexConfig = VortexConfig(xmapMca, ExafsScriptObserver)
# xspress3Config = Xspress3Config(xspress3, ExafsScriptObserver)


sensitivities = [i0_stanford_sensitivity, it_stanford_sensitivity,iref_stanford_sensitivity]
sensitivity_units = [i0_stanford_sensitivity_units,it_stanford_sensitivity_units,iref_stanford_sensitivity_units]
offsets = [i0_stanford_offset,it_stanford_offset,iref_stanford_offset]
offset_units = [i0_stanford_offset_units,it_stanford_offset_units,iref_stanford_offset_units]


#if (LocalProperties.get("gda.mode") == 'live'):
detectorPreparer = B18DetectorPreparer(qexafs_energy, mythen, sensitivities, sensitivity_units ,offsets, offset_units, ionc_gas_injectors.getGroupMembers(), counterTimer01, xspress2system, xmapMca, xspress3)
#else:
#    detectorPreparer = B18DetectorPreparer(qexafs_energy, None, sensitivities, sensitivity_units ,offsets, offset_units, ionc_gas_injectors.getGroupMembers(), xspressConfig, vortexConfig)
samplePreparer = B18SamplePreparer(sam1, sam2, cryo, lakeshore, eurotherm, pulsetube, samplewheel, userstage)
outputPreparer = B18OutputPreparer(datawriterconfig,Finder.getInstance().find("metashop"))
xas = XasScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, datawriterconfig, original_header, energy,Finder.getInstance().find("metashop"), True,False,True)
# qexafs = QexafsScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, original_header, qexafs_energy, qexafs_counterTimer01)
xanes = xas

vararg_alias("xas")
vararg_alias("xanes")
vararg_alias("qexafs")
alias("vortex")
alias("xspress")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
alias("meta_clear_alldynamical")


from gda.jython.commands.ScannableCommands import cv as cvscan
vararg_alias("cvscan")
vararg_alias("cv")

print "Create topup, beam and mono motor temperature monitors to pause and resume scans"
topupMonitor = TopupChecker()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(5)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(60)
topupMonitor.setScannableToBeMonitored(topup)

beamMonitor = BeamMonitor()
beamMonitor.setName("beamMonitor")
beamMonitor.setMachineModeMonitor(machineModeMonitor)
beamMonitor.setShutterPV("FE18B-PS-SHTR-02:STA")
beamMonitor.setPauseBeforeScan(True)     # for qexafs, test FE and machine current at the start of each scan
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
    
    run "userStartupScript"
else :
    print "Moving dummy DCM's to useful positions..."
    energy(7000) # start the simulation with an energy in a useful range
    qexafs_energy(7000)
    print "...moves done";
print "Initialization Complete";
