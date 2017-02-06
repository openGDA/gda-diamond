from gda.configuration.properties import LocalProperties

# Add config/scripts to import search path (why is this not already set in gda9?). 
# Also, this seems to be different to run search path... imh 11/11/2016
import sys 
import os
scriptDir=LocalProperties.get("gda.config")+"/scripts/"
sys.path.append(os.path.abspath(scriptDir))

from andormap import AndorMap
from andormapWithCorrection import AndorMapWithCorrection
from scanForImageCorrection import ScanForImageCorrection
from energyStepScan import EnergyStepScan

print "Initialisation Started";
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, run, alias

def ls_scannables():
    ls_names(Scannable)

from gda.factory import Finder
finder = Finder.getInstance()

from ScannableInvertedValue import PositionInvertedValue
photoDiode1Inverted = PositionInvertedValue("photoDiode1Inverted","photoDiode1")

alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()  # @UndefinedVariable

from gdascripts.pd.time_pds import waittimeClass, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime=waittimeClass('waittime')
showtime=showtimeClass('showtime')
inctime=showincrementaltimeClass('inctime')
actualTime=actualTimeClass("actualTime")

#if (LocalProperties.get("gda.mode") == 'live'):
#    beamMonitor.configure()
#    add_default beamMonitor
#    add_default topupMonitor

# create the command to run STXM mpas which involve andor
andormap = AndorMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor)  # @UndefinedVariable

alias("andormap")
print "Command andormap(mapSize) created for arming the Andor detector before running STXM maps"

#To obtain the corrected images just use the collection strategy for step scan
scanForImageCorrection = ScanForImageCorrection(andor)  # @UndefinedVariable
andormapWithCorrection = AndorMapWithCorrection(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor,scanForImageCorrection)  # @UndefinedVariable
alias("andormapWithCorrection")

# if (LocalProperties.get("gda.mode") == 'live'):
#     run(scriptDir+"xrfmap.py")
#     LocalProperties.set("gda.scan.executeAtEnd","/dls_sw/i08/software/gda/config/scripts/I08_NeXus_Fix.sh")
# else:
LocalProperties.set("gda.scan.executeAtEnd",None)

#energyStepScan = EnergyStepScan(IDEnergy,xmapMca)  # @UndefinedVariable
#alias("energyStepScan")

# Property so that user can drag ROIs in FluorescenceDetector views. imh 11/11/2016
LocalProperties.set("exafs.editor.overlay.Preference", "True")

# For access to new mscan mapping scan command. imh 11/11/2016
print "Adding mscan mapping scan command. Use help(mscan) to get information on how to use it."
run('mapping_scan_commands.py')

# Allow control of the function that maps energy to zone plate position
energyFocusFunction = finder.find("energyFocusFunction")
energyFocusFunction.slopeDividend="-12.132765 um"
energyFocusFunction.interception="25528.85 um"

print "Initialisation Complete";
