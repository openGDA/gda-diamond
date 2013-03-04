#localStation.py
#For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (i05).";
print

print "Importing generic features...";
import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup
from time import sleep
from gda.jython.commands.GeneralCommands import alias


# Get the location of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config")+"/scripts/"
gdascripts = LocalProperties.get("gda.install.git.loc")+"/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

execfile(gdascripts + "/pd/epics_pds.py");
execfile(gdascripts + "/pd/time_pds.py");
execfile(gdascripts + "/pd/dummy_pds.py");
execfile(gdascripts + "/utils.py");

print "Creating beamline specific devices...";
#execfile(gdaScriptDir + "TopupCountdown.py")

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

#01,03,04,06,07,09
gauge01=DisplayEpicsPVClass("gauge01","BL05I-VA-GAUGE-01:P","","%.3e")
gauge03=DisplayEpicsPVClass("gauge03","BL05I-VA-GAUGE-03:P","","%.3e")
gauge04=DisplayEpicsPVClass("gauge04","BL05I-VA-GAUGE-04:P","","%.3e")
gauge06=DisplayEpicsPVClass("gauge06","BL05I-VA-GAUGE-06:P","","%.3e")
gauge07=DisplayEpicsPVClass("gauge07","BL05I-VA-GAUGE-07:P","","%.3e")
gauge09=DisplayEpicsPVClass("gauge09","BL05I-VA-GAUGE-09:P","","%.3e")

#from installStandardScansWithProcessing import *
#scan_processor.rootNamespaceDict=globals()

import metadatatweaks
getTitle = metadatatweaks.getTitle
alias("getTitle")
setTitle = metadatatweaks.setTitle
alias("setTitle")
getVisit = metadatatweaks.getVisit
alias("getVisit")
setVisit = metadatatweaks.setVisit
alias("setVisit")

from arpesmonitor import ARPESMonitor
am=ARPESMonitor()

print "==================================================================="
