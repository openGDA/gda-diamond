from gda.configuration.properties import LocalProperties
from gda.util.persistence import LocalJythonShelfManager
from gda.util.persistence import ObjectShelfException
from gda.factory import Finder
import os


def setDatadirPropertyFromPersistanceDatabase():
	shelf=LocalJythonShelfManager.open("properties")
	try:
		newpath = shelf['gda.data.scan.datawriter.datadir']
		datadir(newpath)
		print "Restored datadir to: "+ LocalProperties.getPath("gda.data.scan.datawriter.datadir",None) 
	except ObjectShelfException, e:
		print "WARNING: Could not restore datadir from database; using the local property gda.data.scan.datawriter.datadir."


def datadir(newpath=None):
	# Reads or sets the data directory
	if newpath==None:
		return LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)
	else:
		if not os.path.exists(newpath):
			print "WARNING: This directory does NOT exist! (pointing to it anyway though)"

		#print "Setting gda.data.scan.datawriter.datadir preference..."
		LocalProperties.set("gda.data.scan.datawriter.datadir", newpath)
		shelf=LocalJythonShelfManager.open("properties")
		shelf['gda.data.scan.datawriter.datadir'] = newpath
		setPildir(newpath)
		setAndorDir(newpath)
		setFirecamDir(newpath)
		setTerminalLoggerDir(newpath)
		return LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)


def setTerminalLoggerDir(newdir):
	newpath = os.path.join(newdir, 'gdaterminal.log')
	tpp = Finder.getInstance().find("terminallog_path_provider")
	print "new record log: ", newpath
	tpp.setPath(newpath)

def setPildir(newpath):
	## Try to set pilatus scannable (it may not exist) ##
	print "pil100kdet.setFilepath('%s/pilatus100k/')"%newpath
	try:
		global pil100kdet
		pil100kdet.setFilePath(newpath + '/pilatus100k/')
	except NameError, _:
		print "   No pil100k scannable found to set path"
	
	print "pil2mkdet.setFilepath('%s/pilatus2M/')"%newpath	
	try:
		global pil2mdet
		pil2mdet.setFilePath(newpath + '/pilatus2M/')
	except NameError, _:
		print "   No pil2m scannable found to set path"	

def setAndorDir(newpath):
	andorpath = newpath + '/andor'
	if not os.path.exists(andorpath):
		os.makedirs(andorpath)
	print "andor1det.setFilepath('%s')"%andorpath
	try:
		global andor1det
		andor1det.setFilePath(andorpath)
	except NameError, _:
		print "   No andorDetector found to set path."

def setFirecamDir(newpath):
	firepath = newpath + '/firecam/'
	if not os.path.exists(firepath):
		os.makedirs(firepath)
	print "firecamDetector.setFilepath('%s')"%firepath
	try:
		global firecamDetector
		firecamDetector.setFilepath(firepath)
	except NameError, _:
		print "   No firecamDetector found to set path."

def visit(visitname=None):
	# Reads or sets the data directory based only on the visit name or run number
	ROOT = "/dls/i16/data/2010/"
	if visitname == None:
		s = datadir().split(ROOT)[1]
		if s[:4]=='mt0/':
			s=s[4:]
		return s
	else:
		if visitname[:3] == 'run':
			visitname = "mt0/" + visitname
			
		print "Setting datadir to '%s':" % (ROOT+visitname,)
		datadir(ROOT+visitname)


#def visitinfo(visitid=None):
#	ROOT = "/dls/i16/data/2009/"	
#	# If no visitid specified, check with iKitten
#	if visitid == None:
#		
#		# Also display generic info
#		print "\nVisit folders in %s:" %ROOT
#		print "   " + str(os.listdir(ROOT))
#		print "\nCommisioning folders in %s:" %( ROOT+"mx0",)
#		print "   " + str(os.listdir(ROOT+"0-0"))
#		
#		# Check for visit numbert from iKitten
#		f = os.popen('/dls_sw/dasc/bin/iKittenScripts/getCurrentVisit')
#		visitid = f.readline()
#		f.close()
#		if visitid[:2]=='mt':
#			print "\nCurrent visit: %s (based only on date and time)"
#			visitid = visitid.split('\n')[0]
#		else:
#			print "\nNo visit in progress (based only on date and time)"
#			visitid = None
#		
#	# if visitid was specified or found in iKitten display info about the visit
#	if visitid:
#		print "\nVisit info:"
#		f = os.popen('/dls_sw/dasc/bin/iKittenScripts/getDetailsOfVisit ' + visitid.upper())
#		line = f.readline()
#		while line != '':
#			if (line != '\n') or (line.find('rows selected'==-1)):
#				print line
#			line = f.readline()
#		f.close()

	