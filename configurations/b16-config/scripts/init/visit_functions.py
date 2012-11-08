import os
from gda.util.persistence import LocalJythonShelfManager
from gda.util.persistence import ObjectShelfException
from gda.data import PathConstructor
from gda.factory import Finder
from gdascripts.scannable.detector.dummy.ImageReadingDummyDetector import ImageReadingDummyDetector
import gda.configuration.properties.LocalProperties


def datadir(legacyCheck=None):
	if legacyCheck is not None:
		raise ValueError("The data directory now depends on the visit. Use the 'visit' command to change this.")
	return PathConstructor.createFromDefaultProperty()

def visit(visitString = None):
	'''Sets and persists visit Metadata. Sets detector directories'''
	print "The visit folder is currently hardcoded in: /dls_sw/b16/software/gda_versions/gda_8_12/b16-config/properties/live/java.properties "
	
	if visitString is None:
		return gda.configuration.properties.LocalProperties.get("gda.data.scan.datawriter.datadir")
		#return Finder.getInstance().find("GDAMetadata").getMetadataValue("visit") or LocalProperties.get('gda.defVisit') #bodge as the visit metadata item has failed after the i18 experiment
	# Set and persist
	gda.configuration.properties.LocalProperties.set('gda.manualvisit',visitString)
	gda.configuration.properties.LocalProperties.set('gda.defVisit',visitString)

	shelf=LocalJythonShelfManager.open("properties")
	shelf['gda.manualVisit'] = visitString
	# Set detectors
	setDetectorDir(PathConstructor.createFromDefaultProperty())
	# Report
	if not os.path.exists(PathConstructor.createFromDefaultProperty()):
		print "   WARNING: The directory '%s' does NOT exist! (pointing to it anyway though)" %PathConstructor.createFromDefaultProperty()
	#return Finder.getInstance().find("GDAMetadata").getMetadataValue("visit") or LocalProperties.get('gda.defVisit') # bodge as above
	return gda.configuration.properties.LocalProperties.get("gda.data.scan.datawriter.datadir")

def restoreVisitSettingFromPersistanceDatabase():
	shelf=LocalJythonShelfManager.open("properties")
	try:
		visit(shelf['gda.manualVisit'])
		print "Restored visit to: ", visit()
	except ObjectShelfException, e: #@UnusedVariable
		print "WARNING: Could not restore visit from database"

def setPildir(newpath):
	## Try to set pilatus scannable (it may not exist) ##
	pilpath = os.path.join(newpath, 'pilatus100k') + '/' # Required by epics
	debug = False
	if debug: print "pildet.setFilepath('%s')"%pilpath
	try:
		global pildet
		pildet.setFilepath(pilpath)
	except NameError:
		if debug: print "   No pil scannable found to modify"

def setIPPDir(newpath):
	debug = False
	if not os.path.exists(newpath+"/ippimages"):
		if debug: print "Creating directory (from the gda server perspective): ", newpath+"/ippimages"
		try:
			os.mkdir(newpath+"/ippimages")
		except:
			pass #At Kawal's insistance!
	new_windows_path = newpath.replace("/dls/b16/data", "N:")+"/ippimages"
	if debug: print "   Setting ippws4.outputFolderRoot to: ", new_windows_path
	global ippws4
	if not isinstance(ippws4, ImageReadingDummyDetector):
		ippws4.setOutputFolderRoot(new_windows_path)

def setIPPWrapperDir(newpath):
	ipp.root_datadir = newpath #@UndefinedVariable

def setDetectorDir(path):
	setIPPDir(path)
	setIPPWrapperDir(path)
	setPildir(path)