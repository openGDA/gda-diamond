print(""*100);
print("="*100);
print "Performing general initialisation code for i05-shared";
print("")

import java #@UnusedImport #@UnresolvedImport
import array #@UnusedImport
from time import sleep, localtime #@UnusedImport

from gda.configuration.properties import LocalProperties #@UnusedImport

from gda.device.scannable.scannablegroup import ScannableGroup #@UnusedImport

from gda.jython.commands.GeneralCommands import alias #@UnusedImport

from gda.factory import Finder #@UnusedImport

from i05Shared.dirFileCommands import pwd, lwf, nwf, nfn #@UnusedImport

print("-"*100)
print(" Load ArpesRun class from arpes script")
import arpes #@UnusedImport #@UnresolvedImport #uk.ac.gda.arpes.server/scripts/arpes.py
print("")

print("-"*100)
print(" Load scannable group single input class")
from i05Shared.scannableGroupSingleInput import ScannableGroupSingleInput
print("")

print("-"*100)
print "Configuring rawid_phase combined scannable for rawid_lowerphase and rawid_upperphase"
try:
	rawid_lowerphase = Finder.find("rawid_lowerphase")
	rawid_upperphase = Finder.find("rawid_upperphase")
	rawid_phase = ScannableGroupSingleInput('rawid_phase', [rawid_lowerphase, rawid_upperphase])
	rawid_phase.configure()
	print ">>> rawid_phase combined scannable configured"
except:
	print ">>> rawid_phase configuration FAILED"
print("")

print("-"*100)
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
from gdascripts.pd.dummy_pds import * #@UnusedWildImport
print("")

print("-"*100)
print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport
from gdascripts.scannable.timerelated import TimeSinceScanStart, clock, epoch  # @UnusedImport
print("")

print("-"*100)
print "Load utilities: caget(pv), caput(pv,value), attributes(object), "
from gdascripts.utils import * #@UnusedWildImport
print("")

print("-"*100)
print "load common physical constants"
from gdascripts.constants import * #@UnusedWildImport
print("")

print("-"*100)
print(" Loading metadatatweaks")
from i05Shared import metadatatweaks
getSubdirectory = metadatatweaks.getSubdirectory
alias("getSubdirectory")

setSubdirectory = metadatatweaks.setSubdirectory
alias("setSubdirectory")

getVisit = metadatatweaks.getVisit
alias("getVisit")

setVisit = metadatatweaks.setVisit
alias("setVisit")
print("")

print("-"*100)
print "Loading Secondary Scannable Group Creator Script... "
print "Usage: scan_creator = ScanCreator(start, stop, step, input_list)"
print "scan_creator.create_group_and_tuples()"
from gdascripts.scan.pathscanCommand import pathscan #@UnusedImport
from i05Shared.pathscanTable import pathscanTable #@UnusedImport
from i05Shared.scan_creator import * #@UnusedWildImport
print("")

print("-"*100)
print "Installing archiver client"
from gdascripts.archiver.archiver import archive  #@UnusedImport
alias('archive')
print("")

# Make time scannable
# Example: scan timeScannable 0 3600 30 analyser - Make a scan starting now, for 1 hour, recording the analyser every 30 secs
print("-"*100)
print(" Creating timeScannable")
timeScannable = TimeSinceScanStart('timeScannable')

print("-"*100)
print "Finished general initialisation code for i05-shared.";
print("")