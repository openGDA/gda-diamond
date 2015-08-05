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
from time import sleep, localtime
from gda.jython.commands.GeneralCommands import alias
from gdascripts.pd.time_pds import actualTimeClass

# Get the location of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config")+"/scripts/"
gdascripts = LocalProperties.get("gda.install.git.loc")+"/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

execfile(gdascripts + "/pd/epics_pds.py");

execfile(gdascripts + "/pd/time_pds.py");
class actTimeInInt(actualTimeClass):  # specialise to make displayed time semi-human-readable
   def rawGetPosition(self):
      pad = 10000
      t = localtime(time.time())      # t = localtime(super(actualTimeClass, self).rawGetPosition())
      tInInt = ((((((t[0]*100+t[1])*100+t[2])*pad+t[3])*100+t[4])*pad)+t[5])
      return tInInt                   # actual wall clock date & time
actTime = actTimeInInt("actTime")       

execfile(gdascripts + "/pd/dummy_pds.py");

execfile(gdascripts + "/utils.py");

print "Creating beamline specific devices...";

gauge01=DisplayEpicsPVClass("gauge01","BL05I-VA-GAUGE-01:P","","%.3e")
gauge03=DisplayEpicsPVClass("gauge03","BL05I-VA-GAUGE-03:P","","%.3e")
gauge04=DisplayEpicsPVClass("gauge04","BL05I-VA-GAUGE-04:P","","%.3e")
gauge06=DisplayEpicsPVClass("gauge06","BL05I-VA-GAUGE-06:P","","%.3e")
gauge07=DisplayEpicsPVClass("gauge07","BL05I-VA-GAUGE-07:P","","%.3e")
gauge09=DisplayEpicsPVClass("gauge09","BL05I-VA-GAUGE-09:P","","%.3e")

import metadatatweaks
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

import arpes
execfile(gdascripts + "scan/pathscanCommand.py");
from pathscanTable import pathscanTable

execfile(gdaScriptDir + "/installStandardScansWithProcessing.py");

print "==================================================================="
if LocalProperties.get("gda.mode")=="live":  # don't execute in squish tests
   print "Running i05 scripts."
   run "beamline/master.py"
print "==================================================================="
