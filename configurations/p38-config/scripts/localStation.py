#localStation.py
#For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (p38).";
print

print "Importing generic features...";
import java
from time import sleep
from gda.jython.commands.GeneralCommands import alias
import logging

from setup.subdirectory import *
logger = logging.getLogger('localStation')

alias('fs')

try:
	print 'Running beamline staff configuration (localStationStaff.py)'
	run('localStationStaff.py')
except Exception as e:
	print 'Error running beamline staff configuration'
	print e
	logger.error('Failed to run beamline staff configuration', exc_info=True)

gdascripts = "/dls_sw/p38/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

execfile(gdascripts + "/pd/epics_pds.py")
execfile(gdascripts + "/pd/time_pds.py")
execfile(gdascripts + "/pd/dummy_pds.py")
execfile(gdascripts + "/utils.py")

from setup.installStandardScansWithProcessing import *
scan_processor.rootNamespaceDict=globals()

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


from gdascripts.pd.time_pds import actualTimeClass
epoch=actualTimeClass("epoch")
print "==================================================================="
