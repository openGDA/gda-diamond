#localStation.py
#For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (b21).";
print

print "Importing generic features...";
import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup
from time import sleep
from gda.jython.commands.GeneralCommands import alias


# Get the locatation of the GDA beamline script directory
gdaScriptDir = "/dls_sw/b21/software/gda/config/scripts/"
gdascripts = "/dls_sw/b21/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

execfile(gdascripts + "/pd/epics_pds.py");
execfile(gdascripts + "/pd/time_pds.py");
execfile(gdascripts + "/pd/dummy_pds.py");
execfile(gdascripts + "/utils.py");
execfile(gdaScriptDir + 'bsaxs_table.py')

print "Creating beamline specific devices...";
execfile(gdaScriptDir + "TopupCountdown.py")

# bsdiode=DisplayEpicsPVClass('bsdiode', 'BL22I-RS-ABSB-02:DIODE:I', '', '%5.5g')
# d10d1=DisplayEpicsPVClass('d10d1', 'BL22I-DI-PHDGN-10:DIODE1:I', '', '%5.5g')
# d10d2=DisplayEpicsPVClass('d10d2', 'BL22I-DI-PHDGN-10:DIODE2:I', '', '%5.5g')

# i0xplus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD1:I_C","ua","%.3e")
# i0xminus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD2:I_C","ua","%.3e")
# i0yplus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD3:I_C","ua","%.3e")
# i0yminus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD4:I_C","ua","%.3e")
# i0=DisplayEpicsPVClass("i0","BL22I-DI-IAMP-06:INTEN_C","ua","%.3e")

# s2xplusi=DisplayEpicsPVClass("s2xplusi","BL22I-AL-SLITS-02:X:PLUS:I:FFB","","%.3e")
# s2yplusi=DisplayEpicsPVClass("s2yplusi","BL22I-AL-SLITS-02:Y:PLUS:I:FFB","","%.3e")
# s2xminusi=DisplayEpicsPVClass("s2xminusi","BL22I-AL-SLITS-02:X:MINUS:I:FFB","","%.3e")
# s2yminusi=DisplayEpicsPVClass("s2yminusi","BL22I-AL-SLITS-02:Y:MINUS:I:FFB","","%.3e")

# from linkam import Linkam
# linkam=Linkam("linkam","BL22I-EA-TEMPC-01")
# from linkamrampmaster4000 import LinkamRampMaster4000
# lrm4k=LinkamRampMaster4000("lrm4k",linkam)

from installStandardScansWithProcessing import *
scan_processor.rootNamespaceDict=globals()

# from redux import NcdRedux
# ncdredux = NcdRedux(ncddetectors)

# preseed listener dispatcher
finder.find("ncdlistener").monitorLive("Saxs Plot", "SAXS")
finder.find("ncdlistener").monitorLive("Waxs Plot", "WAXS")
## import gridscan
## 
## print "Create ncdgridscan"
## try:
## del(gridxy)
## except:
## pass
## gridxy=ScannableGroup()
## gridxy.setName("gridxy")
## gridxy.setGroupMembers([mfstage_x, mfstage_y])
## gridxy.configure()
## ncdgridscan=gridscan.Grid("Camera View", "Mapping Grid", mfgige, gridxy, ncddetectors)
## ncdgridscan.snap()
from ncdutils import DetectorMeta, DetectorMetaString
waxs_distance = DetectorMeta("waxs_distance", ncddetectors, "WAXS", "distance", "m")
saxs_distance = DetectorMeta("saxs_distance", ncddetectors, "SAXS", "distance", "m")
saxs_centre_x = DetectorMeta("saxs_centre_x", ncddetectors, "SAXS", "beam_center_x")
saxs_centre_y = DetectorMeta("saxs_centre_y", ncddetectors, "SAXS", "beam_center_y")
saxs_mask = DetectorMetaString('saxs_mask', ncddetectors, 'SAXS', 'maskFile')

run("energy.py")

import metadatatweaks
getTitle = metadatatweaks.getTitle
alias("getTitle")
setTitle = metadatatweaks.setTitle
alias("setTitle")
getSubdirectory = metadatatweaks.getSubdirectory
alias("getSubdirectory")
setSubdirectory = metadatatweaks.setSubdirectory
alias("setSubdirectory")
getVisit = metadatatweaks.getVisit
alias("getVisit")
setVisit = metadatatweaks.setVisit
alias("setVisit")

import uk.ac.gda.server.ncd.config.DeviceLister
import gda.util.ElogEntry
string = uk.ac.gda.server.ncd.config.DeviceLister.generateDeviceListHTML()
gda.util.ElogEntry.postAsyn("device list from gda", string, "gda", None, "BLB21", "BLB21-RUNL", None)

print 'Importing fast shutter control: fs'
from tfgsetup import fs
print "==================================================================="
