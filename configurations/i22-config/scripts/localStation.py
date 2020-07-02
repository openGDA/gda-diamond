#localStation.py
#For beamline specific initialisation code.
#
from gdaserver import ncddetectors
print "===================================================================";
print "Performing beamline specific initialisation code (i22).";
print

print "Importing generic features...";
import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup
from time import sleep
from gda.factory import Finder
from gda.jython.commands.GeneralCommands import alias
from setup.tfgsetup import setupTfg, addGroup, tfgGroups, fs
from setup.ncddetectorConfig import NcdChannel
import logging
logger = logging.getLogger('localStation')

alias('fs')

try:
	print 'Running beamline staff configuration (localStationStaff.py)'
	run('localStationStaff.py')
except Exception as e:
	print 'Error running beamline staff configuration'
	print e
	logger.error('Failed to run beamline staff configuration', exc_info=True)


# Get the locatation of the GDA beamline script directory
gdaScriptDir = "/dls_sw/i22/software/gda/config/scripts/"
setupScriptDir = "setup/"
#beamlineScriptDir = "beamlineScripts/"

gdascripts = "/dls_sw/i22/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

execfile(gdascripts + "/pd/epics_pds.py")
execfile(gdascripts + "/pd/time_pds.py")
execfile(gdascripts + "/pd/dummy_pds.py")
execfile(gdascripts + "/utils.py")

#Set up the Bimorph Mirror 
#print "Setting up access to Bimorph Mirror Channels...";
run(setupScriptDir + "fastshuttershutter.py")
#execfile(gdaScriptDir + "fastshuttershutter.py")
run(setupScriptDir +  "notchrissbimorph.py")
#execfile(gdaScriptDir + "notchrissbimorph.py")

#execfile(gdaScriptDir + "LookupTables.py")
run(setupScriptDir + "LookupTables.py")
#execfile(gdaScriptDir + "CheckShutter.py");

# '''i0xplus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD1:I_C","ua","%.3e")
# i0xminus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD2:I_C","ua","%.3e")
# i0yplus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD3:I_C","ua","%.3e")
# i0yminus=DisplayEpicsPVClass("i0xplus","BL22I-DI-IAMP-06:PHD4:I_C","ua","%.3e")
# i0=Displa'''yEpicsPVClass("i0","BL22I-DI-IAMP-06:INTEN_C","ua","%.3e")

run(setupScriptDir +  "TopupCountdown.py")
#run(setupScriptDir +  "gainpds.py")
#run(setupScriptDir +  "microfocus.py")

from sampleEnvironment.linkam import Linkam
linkam=Linkam("linkam","BL22I-EA-TEMPC-01")
from sampleEnvironment.linkamrampmaster4000 import LinkamRampMaster4000
lrm4k=LinkamRampMaster4000("lrm4k",linkam)

from setup.installStandardScansWithProcessing import *
scan_processor.rootNamespaceDict=globals()


# preseed listener dispatcher
print "Pre-seeding listener dispatcher"
Finder.find("ncdlistener").monitorLive("Saxs Plot", "SAXS")
Finder.find("ncdlistener").monitorLive("Waxs Plot", "WAXS")

#finding post processing runner
autoPostProcessing = Finder.find('autoPostProcessing')

#hexapod pivot
#execfile(gdaScriptDir + "hexapod.py")

#create cam1, peak2d
#scan slit start end step cam1 620 peak2d
#run "setupBimorphOptimisation"
run(setupScriptDir + "energy.py")
from setup import gridscan

print "Create ncdgridscan"
try:
	del(gridxy)
except:
	pass

try:
	gridxy=ScannableGroup()
	gridxy.setName("gridxy")
	if 'gridscan_stage' in globals():
		stage = globals()['gridscan_stage']
	else:
		stage = [mfstage_x, mfstage_y]
	gridxy.setGroupMembers(stage)
	gridxy.configure()
	ncdgridscan=gridscan.Grid("Microscope View", "Mapping Grid", d13gige, gridxy, ncddetectors)
	ncdgridscan.snap()
except Exception as e:
	print "Could not configure ncdgridscan"
	print '    ' + str(e)

try:
	from ncdutils import DetectorMeta
	saxs_abs_cal = DetectorMeta('saxs_abs_cal', ncddetectors, 'SAXS', 'scaling_factor')
except Exception as e:
	print "Couldn't create saxs_abs_cal"
	print '    ' + str(e)

try:
	from setup import metadatatweaks
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
	setSampleBackground = metadatatweaks.setSampleBackground
	alias("setSampleBackground")
	getSampleBackground = metadatatweaks.getSampleBackground
	alias("getSampleBackground")
	sample_name=metadatatweaks.SampleNameScannable("sample_name","samplename")
except:
	print "Could not set up metadatatweaks"

import bslUtils
bslUtils.restore()
print '\t%sconverting to BSL' %('' if bslUtils.isConvertingOn() else 'not ',)

#run("BeamlineScripts/master.py")

# Temporarily don't run rate.py, meaning the DetGuard object isn't set up.
# This is because it's closing the shutter when beamline staff think it shouldn't
run(setupScriptDir +  "rate.py")

from gdascripts.pd.time_pds import actualTimeClass
epoch=actualTimeClass("epoch")

import uk.ac.gda.server.ncd.config.DeviceLister
import gda.util.ElogEntry
string = uk.ac.gda.server.ncd.config.DeviceLister.generateDeviceListHTML()
gda.util.ElogEntry.postAsyn("device list from gda", string, "gda", None, "BLI22", "BLI22-RUNL", None)
print "importing bimorph"
import bimorph

try:
    for channel, conf in scaler_channels.items():
        for det in ncddetectors.detectors:
            if det.name == channel:
                det.channel = conf.channel
                det.scalingAndOffset = conf.scaling
except NameError as ne:
    print 'No user configuration for It and I0. Using defaults'
except Exception as e:
    print 'Could not apply user settings for It/I0'
    print '    ' + str(e)

#print "creating sampleCam and adding to ncdDetectors"
#execfile(gdaScriptDir + "sampleCam.py")
#run(setupScriptDir + "ZebraDetectors.py")
print "==================================================================="
