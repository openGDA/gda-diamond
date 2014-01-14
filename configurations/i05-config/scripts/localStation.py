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

#from gdascripts.scan import gdascans
#rscan=gdascans.Rscan([])
#alias('rscan');print rscan.__doc__.split('\n')[2]

# Get the location of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config")+"/scripts/"
gdascripts = LocalProperties.get("gda.install.git.loc")+"/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

execfile(gdaScriptDir + "/installStandardScansWithProcessing.py");

execfile(gdascripts + "/pd/epics_pds.py");
execfile(gdascripts + "/pd/time_pds.py");
execfile(gdascripts + "/pd/dummy_pds.py");
execfile(gdascripts + "/utils.py");

print "Creating beamline specific devices...";
#execfile(gdaScriptDir + "TopupCountdown.py")

# d10d1=DisplayEpicsPVClass('d10d1', 'BL22I-DI-PHDGN-10:DIODE1:I', '', '%5.5g')
# d10d2=DisplayEpicsPVClass('d10d2', 'BL22I-DI-PHDGN-10:DIODE2:I', '', '%5.5g')

s2xplus=DisplayEpicsPVClass('s2xplus', 'BL05I-AL-SLITS-02:X:PLUS:I', '', '%5.5g')
s2xminus=DisplayEpicsPVClass('s2xminus', 'BL05I-AL-SLITS-02:X:MINUS:I', '', '%5.5g')
s2yplus=DisplayEpicsPVClass('s2yplus', 'BL05I-AL-SLITS-02:Y:PLUS:I', '', '%5.5g')
s2yminus=DisplayEpicsPVClass('s2yminus', 'BL05I-AL-SLITS-02:Y:MINUS:I', '', '%5.5g')

s3xplus=DisplayEpicsPVClass('s3xplus', 'BL05I-AL-SLITS-03:X:PLUS:I', '', '%5.5g')
s3xminus=DisplayEpicsPVClass('s3xminus', 'BL05I-AL-SLITS-03:X:MINUS:I', '', '%5.5g')
s3yplus=DisplayEpicsPVClass('s3yplus', 'BL05I-AL-SLITS-03:Y:PLUS:I', '', '%5.5g')
s3yminus=DisplayEpicsPVClass('s3yminus', 'BL05I-AL-SLITS-03:Y:MINUS:I', '', '%5.5g')

s5xplus=DisplayEpicsPVClass('s5xplus', 'BL05I-AL-SLITS-05:X:PLUS:I', '', '%5.5g')
s5xminus=DisplayEpicsPVClass('s5xminus', 'BL05I-AL-SLITS-05:X:MINUS:I', '', '%5.5g')
s5yplus=DisplayEpicsPVClass('s5yplus', 'BL05I-AL-SLITS-05:Y:PLUS:I', '', '%5.5g')
s5yminus=DisplayEpicsPVClass('s5yminus', 'BL05I-AL-SLITS-05:Y:MINUS:I', '', '%5.5g')

#d3current=DisplayEpicsPVClass('d3current', 'BL05I-DI-PHDGN-03:DET:I', '', '%5.5g')
#d7current=DisplayEpicsPVClass('d7current', 'BL05I-DI-PHDGN-07:DET:I', '', '%5.5g')
#d9current=DisplayEpicsPVClass('d9current', 'BL05I-DI-PHDGN-08:DET:I', '', '%5.5g')
#dj7current=DisplayEpicsPVClass('dj7current', 'BL05J-DI-PHDGN-02:DET:I', '', '%5.5g')

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

d10xpos=DisplayEpicsPVClass("d10xpos","BLI05-DI-PHDGN-10:DCAM:STAT:CentroidX_RBV","","%.3e")
d10ypox=DisplayEpicsPVClass("d10ypos","BLI05-DI-PHDGN-10:DCAM:STAT:CentroidY_RBV","","%.3e")

#from installStandardScansWithProcessing import *
#scan_processor.rootNamespaceDict=globals()

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
def isgold():
   return saz.getPosition() < -18
sample_name=metadatatweaks.SampleNameScannable("sample_name","samplename",isgoldpost=isgold)

from arpesmonitor import ARPESMonitor
am=ARPESMonitor()
centre_energy=analyser.getCentreEnergyScannable()
centre_energy.setName("centre_energy")
centre_energy.setInputNames(["centre_energy"])

caput("BL05I-EA-DET-01:ARR1:EnableCallbacks",1)

print "==================================================================="
print "Running i05 scripts."
run "beamline/master.py"
print "==================================================================="
