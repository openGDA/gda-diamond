import sys;
import string;
import os.path
import java
from java.lang import Math, String
from time import sleep
from time import localtime
import gda
import gda.factory.Finder as Finder;
from gda.device.epicsdevice import ReturnType
from gda.util import VisitPath
from gda.analysis import ScanFileHolder
from gda.jython import InterfaceProvider
from gda.jython import JythonServerFacade
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.parameters import beamline_parameters
import LookupTables

from dummy_scan_objects import SimpleDummyDetector, SimpleDummyMotor

def checkEpicsDevices():
	"""reloads all lookup tables on the ObjectServer"""
	ok = True
	finder = Finder.getInstance()
	epicsDevices = finder.listAllObjects("IEpicsDevice")
	if(len(epicsDevices) != 88):
		print "Error number of devices != 88. Actual number = " + `len(epicsDevices)`
		ok = False
	for epicsDevice in epicsDevices:
		if epicsDevice.getName() == "Beamline":
#			print epicsDevice
			continue
		records = epicsDevice.getAttribute("Records")
		for record in records:
			try:
#				print epicsDevice, record, epicsDevice.getValue(ReturnType.DBR_NATIVE, record,"")
				val = epicsDevice.getValue(ReturnType.DBR_NATIVE, record,"")
			except:
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"Error calling getValue for " + `epicsDevice` + ":" + `record`,
					type, exception, None, False)
				ok = False
	return ok

def checkOE(jythonNameMap, oeName, expectedDOFNames):
	ok = True
	try:
		oe = jythonNameMap.__getattr__(oeName)
		dofNames = oe.getDOFNames()
		if(len(dofNames) != len(expectedDOFNames)):
			print "Error - number of  dofs != numberExpected  for " + oe.getName()
			ok = False
		for dofName in expectedDOFNames:
			try:
				val = oe.getPosition(dofName)
				dof = jythonNameMap.__getattr__(dofName)
				dofval = dof()
				if( java.lang.Double.isNaN(dofval)):
					print oe.getName()+"."+dofName + " = NaN"
					ok = False
#				print dofName, val, dof()
			except:
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"Error checking " + oe.getName()+"."+ dofName,
					type, exception, None, False)
				ok = False
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking oe  " + oeName, type, exception, None, False)
		ok = False
	
	return ok

def checkOEs(jythonNameMap, finderNameMap):
	
	ok = True
	ok = checkOE(jythonNameMap,"BS", ["bsx", "bsy"] ) and  ok
	ok = checkOE(jythonNameMap,"Diffractometer", ['dx', 'dy', 'dz', 'dkphi', 'dkappa', 'dktheta', 'dmu', 'ddelta', 'dgamma', 'djack1', 'djack2', 'djack3', 'dtransx', 'drotation' ] ) and  ok
	ok = checkOE(jythonNameMap,"EHT2", ['eht2theta', 'eht2dtx']) and  ok
	ok = checkOE(jythonNameMap,"M1", ['vfm_pitch', 'vfm_y', 'vfm_yaw', 'vfm_x', 'vfm_curve', 'vfm_ellipticity']) and  ok
	ok = checkOE(jythonNameMap,"M2", ['hfm_pitch', 'hfm_y', 'hfm_yaw', 'hfm_x', 'hfm_roll', 'vfm_curve', 'hfm_ellipticity']) and  ok
	ok = checkOE(jythonNameMap,"PinHole", ['pinx', 'piny', 'pinz']) and  ok
	ok = checkOE(jythonNameMap,"S1", ['s1xpos', 's1xgap', 's1ypos', 's1ygap', 's1xplus', 's1xminus', 's1yplus', 's1yminus']) and  ok
	ok = checkOE(jythonNameMap,"S4", ['s4xpos', 's4xgap', 's4ypos', 's4ygap'] ) and  ok
	ok = checkOE(jythonNameMap,"TestOE", ['testLinearDOF1', 'testLinearDOF2', 'testAngularDOF1', 'testAngularDOF2', 'testCombinedDOF1', 'testCombinedDOF2'] ) and  ok
	return ok


def checkAdc(finderNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		obj.getGain()
		obj.getOffset()
		obj.getLld()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking adc  " + name, type, exception, None, False)
		ok = False
	return ok

def checkAdcs(finderNameMap):
	
	ok = True
	ok = checkAdc(finderNameMap,"epicsAdc01") and ok
	return ok

def checkCounterTimer(jythonNameMap, name, expectedReadoutSize):
	ok = True
	try:
		obj = jythonNameMap.__getattr__(name)
		obj.setCollectionTime(1.0)
		obj.collectData()
		if ( not obj.isBusy()):
			raise "Error - counterTimer is not busy following countAsync call"
		sleep(2.0)
		if ( obj.isBusy()):
			raise "Error - counterTimer is still busy after waiting 2s. - Check realtime/live time balance."
		data = obj.readout()
		if isinstance( obj , gda.device.detector.EpicsMCACounterTimer):
			length = len( data[0] )
		else:
			length = len( data )
		if( length  != expectedReadoutSize):
			raise "Error - readoutSize = " + `length`
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking counterTimer  " + name, type, exception, None, False)
		ok = False
	return ok

def checkCounterTimers(jythonNameMap):
	
	ok = True
	ok = checkCounterTimer(jythonNameMap,"Vortex1_MCAScaler", 32) and ok
	ok = checkCounterTimer(jythonNameMap,"Vortex1_Scaler", 32) and ok
	return ok

def checkAnalyser(finderNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		if isinstance( obj, gda.device.EpicsTca): 
			obj.getAttribute("SCA1HI")
			obj.getAttribute("energyToChannel10000 eV")
		elif isinstance(obj, gda.device.detector.analyser.EpicsMCA):
			obj.getNumberOfRegions()
			(obj.getPresets()).presetLiveTime
			obj.getAttribute("energyToChannel10000 eV")
			obj.getStatus()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking analyser  " + name, type, exception, None, False)
		ok = False
	return ok

def checkAnalysers(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkAnalyser(finderNameMap,"epicsMca01") and ok
	ok = checkAnalyser(finderNameMap,"epicsTca01") and ok
	return ok

def checkSampleChanger(finderNameMap, jythonNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		obj.numberOfHolders
		obj.samplesPerHolder
		obj.actionApproverName
		approver = jythonNameMap.__getattr__(obj.actionApproverName)
		approver.actionApproved()
		obj.getStatus()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking sampleChanger  " + name, type, exception, None, False)
		ok = False
	return ok

def checkSampleChangers(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkSampleChanger(finderNameMap,jythonNameMap,"PXSampleChanger") and ok
	return ok

def checkBCM(finderNameMap, jythonNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		((obj.getBCMParameters()).getLogin_info()).getDefault_directory()
		((obj.getBCMParameters()).getExperiment()).getWavelength()
		((obj.getBCMParameters()).getDetector()).getSuffix()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkBCM - error  " + name, type, exception, None, False)
		ok = False
	return ok

def checkBCMs(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkBCM(finderNameMap,jythonNameMap,"bcm" ) and ok
	return ok

def checkBCMFinder(jythonNameMap,finderNameMap ):
	ok = True
	try:
		obj = jythonNameMap.__getattr__("BCMFinder")
		obj.getBcm().getName()
		obj.getCamera().getName()
		obj.getCamera().getName()
		obj.getDetector().getName()
		obj.getFileHeader().getName()
		obj.getOpticalCamera().getName()
		obj.getParameters().getName()
		obj.getSampleChanger().getName()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkBCMFinder - error  " + name, type, exception, None, False)
		ok = False
	return ok

def checkCamera(finderNameMap, jythonNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		obj.getCamStatus().getCurrentPosition()
		obj.getDetectorDistance()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkCamera - error  " + name, type, exception, None, False)
		ok = False
	return ok

def checkCameras(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkCamera(finderNameMap,jythonNameMap,"PXCamera" ) and ok
	return ok

def checkDetector(finderNameMap, jythonNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		obj.setAttribute("ImageFileName","TestFileName")
		fileName = obj.getFilename()
		if( fileName != "TestFileName"):
			raise "checkDetector - error setting filename"
		obj.qc.getDetStatus()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkDetector - error  " + name, type, exception, None, False)
		ok = False
	return ok

def checkDetectors(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkDetector(finderNameMap,jythonNameMap,"PXDetector" ) and ok
	return ok

def checkOpticalCamera(finderNameMap, jythonNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		obj.getZoom()
		obj.getZoomLevels()
		obj.getMicronsPerXPixel()
		obj.getMicronsPerYPixel()
		obj.captureImage("/scratch/1.png")
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkOpticalCamera - error  " + name, type, exception, None, False)
		ok = False
	return ok

def checkOpticalCameras(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkOpticalCamera(finderNameMap,jythonNameMap,"OpticalCamera" ) and ok
	return ok

def checkFileHeader(finderNameMap, jythonNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		obj.getBeamX()
		obj.getBeamY()
		obj.getPhiStart()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkFileHeader - error " + name, type, exception, None, False)
		ok = False
	return ok

def checkFileHeaders(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkFileHeader(finderNameMap,jythonNameMap,"PXFileHeader" ) and ok
	return ok

def checkScan2(jythonNameMap,finderNameMap ):
	ok = True
	try:
		scan = gda.scan.ConcurrentScan( [ jythonNameMap.testCombinedDOF2, 1, 10, 1, jythonNameMap.testAngularDOF1 ])
		scan.runScan()
		filepath = VisitPath.getVisitPath() + "/" + scan.getDataWriter().getCurrentFileName()
		data1 = ScanFileHolder()
		data1.loadSRS(filepath)
		max = data1.getMax(jythonNameMap.testAngularDOF1.getName())
		maxX = data1.getMaxPos(jythonNameMap.testCombinedDOF2.getName(), jythonNameMap.testAngularDOF1.getName())
		if( max != 17.956 or maxX != 10):
			raise "Error - max != 17.956 or maxX != 10. Values = " + `max` + ", " + `maxX` + " data in " + `filepath`
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkScan2 - error ", type, exception, None, False)
		ok = False
	return ok

def checkScan1(jythonNameMap,finderNameMap ):
	ok = True
	try:
		gda.scan.ConcurrentScan( [ jythonNameMap.testCombinedDOF1, 1, 10, 1, jythonNameMap.testLinearDOF2 ]).runScan()
		data = ScanFileHolder()
		data.loadSRS()
		max = data.getMax(jythonNameMap.testLinearDOF2.getName())
		maxX = data.getMaxPos(jythonNameMap.testCombinedDOF1.getName(), jythonNameMap.testLinearDOF2.getName())
		if( max != 10 or maxX != 10):
			raise "Error - max != 10 or maxX != 10. Values = " + `max` + ", " + `maxX`
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkScan1 - error ", type, exception, None, False)
		ok = False
	return ok

def checkScannable(jythonNameMap, obj):
	ok = True
	try:
		obj.getPosition()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkScannable - error " + obj.getName(), type, exception, None, False)
		ok = False
	return ok

def checkScannables(jythonNameMap,finderNameMap ):
	ok = True
	numScannables=0
	allObjectNamesString = JythonServerFacade.getInstance().evaluateCommand("dir()")
	allObjectNames = allObjectNamesString.split(",")
	for objectName in allObjectNames:
		objectNameOrig = objectName
		objectName = objectName.replace("[","")
		objectName = objectName.replace("'","")
		objectName = objectName.replace(" ","")
		objectName = objectName.replace("]","")
		try:
			obj = jythonNameMap.__getattr__(objectName)
			if isinstance(obj, gda.device.Scannable):
				numScannables += 1			
				ok = checkScannable(jythonNameMap, obj) and ok
		except:
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None,"checkScannables - error getting attribute " + objectName + " item in namespace = " + objectNameOrig, type, exception, None, False)
			ok = False
	if(numScannables != 8):
		print "Error number of Scannable != 8. Actual number = " + `numScannables`
		ok = False
	return ok


def checkRuby(jythonNameMap,finderNameMap ):
	ok = True
	Test = ""
	try:
		rubyObj = jythonNameMap.ruby
		ccd = finderNameMap.ODCCD
		Test = "Reconnect - if fails re-start IS"
#		ccd.disconnect()
#		rubyObj.connect()
		rubyObj.flush()
		
		Test = "Control shutter"
		rubyObj.openS()
		open = rubyObj.getS()
		rubyObj.closeS()
		close = rubyObj.getS()
		if open != "OPEN":
			raise "Shutter did not open"
		if close != "CLOSED":
			raise "Shutter did not close. Ensure shutter control box is powered on and shutter cable is connected."
			
		Test = "Plot 2x2"
		rubyObj.plot("/dls/i15/software/gda/plugins/uk.ac.gda.core/test/gda/analysis/io/TestFiles/bs_24_1un.img")
		sleep(2)
		Test = "Plot 1x1"
		rubyObj.plot("/dls/i15/software/gda/plugins/uk.ac.gda.core/test/gda/analysis/io/TestFiles/lab_source_35_1x1_corr_mscalar.img")
		
		Test = "Get RunList"
		runListLoader = jythonNameMap.__getattr__("RunListLoader")
		runList = runListLoader().getRunList(ccd, "X:/data/2008/ee0/GDA/garnet","garnet.run")
		if runList.info.getExperimentName() != ' "garnet"':
			raise "ExperimentName is incorrect = " + runList.info.getExperimentName() 
			
		ISfolder = "X:/data/2008/ee0/"
		GDAfolder = "/dls/i15/data/2008/ee0/"
		rubyObj.setDir(ISfolder)
		filenamePrefix = "rubyExpose_bin"
		exposureTime = 1.0
		for bin in range(1,4,1):
			Test = "ruby.expose bin - " + `bin`
			handle_messages.log(None,Test)
			rubyObj.setBin(bin)
			fileName = rubyObj.expose(exposureTime, filenamePrefix+`bin`)
			sleep(exposureTime)
			rubyObj.readImage(None)
			rubyObj.flush()
			sleep(rubyObj.getReadOutDelay())
			rubyObj.plot(GDAfolder + fileName)

	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkRuby - error in test -  " + Test, type, exception, None, False)
		ok = False
	return ok

def checkRubyScripts(jythonNameMap,finderNameMap ):
	ok = True
	Test = ""
	try:
		
		getDir = jythonNameMap.getDir
		setDir = jythonNameMap.setDir
		setFullUserDir = jythonNameMap.setFullUserDir
		fullUserDir = getDir()
		setDir("ee0",0,"testRuby")
		
		rubyObj = jythonNameMap.__getattr__("ruby")
		expose = jythonNameMap.__getattr__("expose")
		simpleScan = jythonNameMap.__getattr__("simpleScan")
		doubleScan = jythonNameMap.__getattr__("doubleScan")
		getNextCCDScanNumber = jythonNameMap.__getattr__("getNextCCDScanNumber")
		rubyObj.setExportAll(0)
		currentYear = localtime()[0]
		
		Test = "test_ruby_expose"
		nextScanNo = getNextCCDScanNumber() + 1
		files = expose(rubyObj, 5, 2, Test, -1, "ya")
		checkFiles(convertToDlsPath(files), ["/dls/i15/data/" + `currentYear` + "/ee0/testRuby/test_ruby_expose__%03d" % nextScanNo + "_001.img", 
											 "/dls/i15/data/" + `currentYear` + "/ee0/testRuby/test_ruby_expose__%03d" % nextScanNo + "_002.img"])

		#motorNames = ["dkphi", "dktheta",  "ddelta",  "dgamma"]
		motorNames = ["dkphi"]
		for motorName in motorNames:
			motor = jythonNameMap.__getattr__(motorName)
	
			Test = "test_ruby_simpleScan_" + motorName 
			files = simpleScan(motor, motor()-0.5, motor()+0.5, 0.5, rubyObj, 5, Test, 33, "ya")
			checkFiles(convertToDlsPath(files), ["/dls/i15/data/" + `currentYear` + "/ee0/testRuby/test_ruby_simpleScan_33_1.img", 
												 "/dls/i15/data/" + `currentYear` + "/ee0/testRuby/test_ruby_simpleScan_33_2.img"])

#			Test = "test_ruby_doubleScan_" + motorName 
#			files = doubleScan(motor, -120, -119, 0.5, rubyObj, 5, Test, 23, "ya")
#			checkFiles(convertToDlsPath(files), ["/dls/i15/data/" + `currentYear` + "/ee0/testRuby/test_ruby_simpleScan_23_1.img", 
#												 "/dls/i15/data/" + `currentYear` + "/ee0/testRuby/test_ruby_simpleScan_23_2.img"])

	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkRubyScripts - error in test -  " + Test, type, exception, None, False)
		ok = False
	setFullUserDir(fullUserDir)
	return ok

def convertToDlsPath(files):
	retFiles = []
	for file in files:
		newDir = file.replace("x:/", "/dls/i15/data/")
		newDir = newDir.replace("X:/", "/dls/i15/data/")
		retFiles.append(newDir)
	return retFiles

def checkFiles(files, expectedFileNames):
	if( len(files) != len(expectedFileNames)):
		print files
		print expectedFileNames
		raise "number of files  - " + `len(files)` + " does not match expected - " + `len(expectedFileNames)`
	for i in range(0, len(expectedFileNames),1):
		if( files[i] != expectedFileNames[i] ):
			raise "Filename - " + files[i] + " does not match expected - " + expectedFileNames[i]
		if not os.path.isfile(files[i]):
			raise "File does not exist - " + files[i]

def checkMarScripts(jythonNameMap,finderNameMap ):
	ok = True
	Test = ""
	getDir = jythonNameMap.__getattr__("getDir")
	setDir = jythonNameMap.__getattr__("setDir")
	setFullUserDir = jythonNameMap.__getattr__("setFullUserDir")
	fullUserDir = getDir()
	
			
	marObj = jythonNameMap.__getattr__("mar")
	expose = jythonNameMap.__getattr__("expose")
	multiExposeScan = jythonNameMap.__getattr__("multiExposeScan")
	rockScan = jythonNameMap.__getattr__("rockScan")
	getNextMarScanNumber = jythonNameMap.__getattr__("getNextMarScanNumber")
	try:
		setDir("ee0",0,"testMar")

		Test = "marErase"
		marErase = jythonNameMap.__getattr__("marErase")
		marErase(1)
		currentYear = localtime()[0]

		Test = "test_mar_expose"
		nextScanNo = getNextMarScanNumber() + 1
		files = expose(marObj, 5, 3, "test_mar_expose", -1, "ya")
		checkFiles(files, ["/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_expose_%03d" % nextScanNo + "_001.mar3450", 
						   "/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_expose_%03d" % nextScanNo + "_002.mar3450", 
						   "/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_expose_%03d" % nextScanNo + "_003.mar3450"])
		
		#motorNames = ["dkphi", "dktheta",  "ddelta",  "dgamma"]
		motorNames = ["dkphi"]
		for motorName in motorNames:
			motor = jythonNameMap.__getattr__(motorName)
			
			Test = "test_mar_multiExposeScan" 
			nextScanNo = getNextMarScanNumber() + 1
			files = multiExposeScan(motor, motor()-0.5, motor()+0.5, 0.5, marObj, 5, 2, Test, -1, "ya")
			checkFiles(files, [ "/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_multiExposeScan_%03d" % nextScanNo + "_001.mar3450", 
								"/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_multiExposeScan_%03d" % nextScanNo + "_002.mar3450", 
								"/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_multiExposeScan_%03d" % (nextScanNo + 1) + "_001.mar3450",
								"/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_multiExposeScan_%03d" % (nextScanNo + 1) + "_002.mar3450" ])
		
			Test = "test_mar_rock"
			nextScanNo = getNextMarScanNumber() + 1
			files = rockScan(motor, motor(), 1, 2, marObj, 1, Test, -1, "ya")
			checkFiles(files, expectedFiles)
			checkFiles(files, [ "/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_rock_%03d" % nextScanNo + "_001.mar3450", 
								"/dls/i15/data/" + `currentYear` + "/ee0/testMar/test_mar_rock_%03d" % nextScanNo + "_002.mar3450" ])

	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkMarScripts - error in test -  " + Test, type, exception, traceback, False)
		ok = False
	setFullUserDir(fullUserDir)
	return ok


def checkScannableGroup(jythonNameMap, groupName, expectedMotorNames):
	ok = True
	try:
		group = jythonNameMap.__getattr__(groupName)
		motorNames = group.getGroupMemberNames()
		if(len(motorNames) != len(expectedMotorNames)):
			print "Error - number of  motors != numberExpected  for " + group.getName()
			ok = False
		for motorName in expectedMotorNames:
			try:
				val = group.getGroupMember(motorName)
				motor = jythonNameMap.__getattr__(motorName)
				motorval = motor()
				if( java.lang.Double.isNaN(motorval)):
					print group.getName()+"."+motorName + " = NaN"
					ok = False
#				print dofName, val, dof()
			except:
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"Error checking " + group.getName()+"."+ motorName,
					type, exception, None, False)
				ok = False
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking scannableGroup  " + groupName, type, exception, None, False)
		ok = False
	
	return ok

def checkScannableGroups(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkScannableGroup(jythonNameMap,"testSG", ["testLinearSM1", "testLinearSM2", "testAngularSM1", "testAngularSM2" ] ) and  ok
	return ok

def checkPilatusPD(jythonNameMap, pilatusPDName):
	ok = True
	getDir = jythonNameMap.__getattr__("getDir")
	setDir = jythonNameMap.__getattr__("setDir")
	setFullUserDir = jythonNameMap.__getattr__("setFullUserDir")
	fullUserDir = getDir()
	setDir("ee0",0,"testPilatus")
	try:
		pilatusPD = jythonNameMap.__getattr__(pilatusPDName)
		pilatusPD.display("/dls/i15/software/gda/test/gda/analysis/io/TestFiles/Pilatus/fcell_H_8GPa_20keV_18000s_0173.tif")
		if pilatusPD.data.getImage()[0][0] != 81.0:
			raise "Value at 0,0 != 81.0"

		oldFilePath = pilatusPD.getFilePath()
		oldFileNumber = pilatusPD.getFileNumber()

		currentYear = localtime()[0]
		pilatusPD.setFilePath("/dls/i15/data/" + `currentYear` + "/ee0/testPilatus/")
		
		expose = jythonNameMap.__getattr__("expose")
		simpleScan = jythonNameMap.__getattr__("simpleScan")
		
		Test = "test_pilatus_expose"
		nextFileNo = int(pilatusPD.getFileNumber())
		files = expose(pilatusPD, 5, 2, Test, -1, "ya")
		checkFiles(files, [ "/dls/i15/data/" + `currentYear` + "/ee0/testPilatus/test_pilatus_expose_%04d" % nextFileNo + ".tif", 
							"/dls/i15/data/" + `currentYear` + "/ee0/testPilatus/test_pilatus_expose_%04d" % (nextFileNo + 1) + ".tif" ])

		#motorNames = ["dkphi", "dktheta",  "ddelta",  "dgamma"]
		motorNames = ["dkphi"]
		for motorName in motorNames:
			motor = jythonNameMap.__getattr__(motorName)
	
			Test = "test_pilatus_simpleScan_" + motorName
			nextFileNo = int(pilatusPD.getFileNumber())
			files = simpleScan(motor, motor()-0.5, motor()+0.5, 0.5, pilatusPD, 5, Test, -1, "ya")
			checkFiles(files, [ "/dls/i15/data/" + `currentYear` + "/ee0/testPilatus/test_pilatus_simpleScan_%04d" % nextFileNo + ".tif", 
								"/dls/i15/data/" + `currentYear` + "/ee0/testPilatus/test_pilatus_simpleScan_%04d" % (nextFileNo + 1) + ".tif"])

		pilatusPD.setFilePath(oldFilePath)
		pilatusPD.setFileNumber(oldFileNumber)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkPilatusPD for   " + pilatusPDName, type, exception, traceback, False)
		ok = False
	setFullUserDir(fullUserDir)
	return ok

def checkPilatusPDs(jythonNameMap,finderNameMap ):
	ok = True
	ok = checkPilatusPD(jythonNameMap,"pilatus" ) and  ok
	ok = checkPilatusPD(jythonNameMap,"pilatusDummy" ) and  ok
	return ok

def checkExposeWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		expose = jythonNameMap.expose
		files = expose(SimpleDummyDetector(), 3, 5)
		checkFiles(files,['//dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_001.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_002.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_003.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_004.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_005.testImage'])
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkExposeWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok

def checkExpose1WithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		from detectorScanScripts import expose1
		files = expose1(SimpleDummyDetector(), 3, 5)
		checkFiles(files,['/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_001.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_002.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_003.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_004.testImage', '/dls/i15/data/gdatest/integrationTests/dummyDetector_expose_055_005.testImage'])
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkExposeWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok

def checkSimpleScanWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		simpleScan = jythonNameMap.simpleScan
		files = simpleScan(SimpleDummyMotor(), 0, 10, 1, SimpleDummyDetector(), 1)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkSimpleScanWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok


def checkSimpleScanUnsyncWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		simpleScanUnsync = jythonNameMap.simpleScanUnsync
		files = simpleScanUnsync(SimpleDummyMotor(), 0, 10, 1, SimpleDummyDetector(), 1)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkSimpleScanUnsyncWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok
	
def checkMultiExposeScanWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		multiExposeScan = jythonNameMap.multiExposeScan
		files = multiExposeScan(SimpleDummyMotor(), 0, 10, 1, SimpleDummyDetector(), 1, 3)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkMultiExposeScanWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok
	
def checkSingleStepScanWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		singleStepScan = jythonNameMap.singleStepScan
		files = singleStepScan(SimpleDummyMotor(), 0, 10, 3, SimpleDummyDetector(), 2)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkSingleStepScanWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok
	
def checkRockScanWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		rockScan = jythonNameMap.rockScan
		files = rockScan(SimpleDummyMotor(), 0, 5, 3, SimpleDummyDetector(), 2)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkRockScanWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok
	
def checkRockScanUnsyncWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		rockScanUnsync = jythonNameMap.rockScanUnsync
		files = rockScanUnsync(SimpleDummyMotor(), 0, 5, 3, SimpleDummyDetector(), 2)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkrockScanUnsyncWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok
	
def checkDoubleScanWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		doubleScan = jythonNameMap.doubleScan
		files = doubleScan(SimpleDummyMotor(), 0, 10, 1, SimpleDummyDetector(), 1)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkDoubleScanWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok

def checkDarkExposeWithDummyHardware(jythonNameMap,finderNameMap):
	ok = True
	try:
		darkExpose = jythonNameMap.darkExpose
		files = darkExpose(SimpleDummyDetector(), 5, 3)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checkDarkExposeWithDummyHardware", type, exception, traceback, False)
		ok = False
	return ok

def checkAll():
	from dataDir import setFullUserDir
	ok = True
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	finderNameMap = beamline_parameters.FinderNameMapping()
	beamlineParameters = beamline_parameters.Parameters()
	
	os.system("rm -rf /dls/i15/data/gdatest/integrationTests")
	setFullUserDir("/dls/i15/data/gdatest/integrationTests");
	
	ok = checkExposeWithDummyHardware(jythonNameMap, finderNameMap) and ok
	ok = checkScannables(jythonNameMap, finderNameMap) and ok
	
	#ok = checkSimpleScanWithDummyHardware(jythonNameMap, finderNameMap) and ok
	#ok = checkSimpleScanUnsyncWithDummyHardware(jythonNameMap, finderNameMap) and ok
	#ok = checkMultiExposeScanWithDummyHardware(jythonNameMap, finderNameMap) and ok
	#ok = checkSingleStepScanWithDummyHardware(jythonNameMap, finderNameMap) and ok
	#ok = checkRockScanWithDummyHardware(jythonNameMap, finderNameMap) and ok	
	#ok = checkRockScanUnsyncWithDummyHardware(jythonNameMap, finderNameMap) and ok#mar not ready error
	#ok = checkDoubleScanWithDummyHardware(jythonNameMap, finderNameMap) and ok
	#ok = checkDarkExposeWithDummyHardware(jythonNameMap, finderNameMap) and ok	
	#ok = checkExpose1WithDummyHardware(jythonNameMap, finderNameMap)and ok
	
	
	#ok = checkScan1(jythonNameMap, finderNameMap) and ok
	#ok = checkScan2(jythonNameMap, finderNameMap) and ok
	
	
#not valid for i15	ok = checkFileHeaders(command_server) and ok
#not valid for i15	ok = checkDetectors(command_server) and ok
#not valid for i15	ok = checkOpticalCameras(command_server) and ok
#not valid for i15	ok = checkCameras(command_server) and ok
#not valid for i15	ok = checkBCMs(command_server) and ok
#not valid for i15	ok = checkBCMFinder(command_server) and ok
#not valid for i15	ok = checkAnalysers(command_server) and ok
#not valid for i15	ok = checkSampleChangers(command_server) and ok
#not valid for i15	ok = checkCounterTimers(command_server) and ok
#not valid for i15	ok = checkAdcs(command_server) and ok

	#ok = checkOEs(jythonNameMap, finderNameMap) and ok
	#ok = checkEpicsDevices() and ok
	#ok = LookupTables.reloadLookupTablesEx(False) and ok
	#ok = checkRuby(jythonNameMap, finderNameMap) and ok   
	
#	ok = checkRubyScripts(jythonNameMap, finderNameMap) and ok
#	ok = checkMarScripts(jythonNameMap, finderNameMap) and ok
#	ok = checkScannableGroups(jythonNameMap, finderNameMap) and ok	
#	ok = checkPilatusPDs(jythonNameMap, finderNameMap) and ok	
	if( not ok):
		print "checkAll completed with error"
	return ok
	
	
	
	
	