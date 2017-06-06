import time
from time import sleep
import glob
from gda.jython.commands.GeneralCommands import pause
from gdascripts.messages.handle_messages import simpleLog
from util_scripts import doesFileExist
import os

global configured, ruby, beamline
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, ruby, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	ruby = jythonNameMap.ruby
	beamline = jythonNameMap.beamline
	configured = True
	
	
def checkConfigured():
	if not configured:
		raise "ccdAuxiliary not configured"
		
#######################################################################################
def getCCDScanNumberPath():
	return getScanNumberPath("/dls_sw/i15/var/nextCCDScanNumber")

#######################################################################################
def getScanNumberPath(pathStub):

	# Try to read from pathStub location
	pathToNextCCDNumberList = glob.glob(pathStub + ".*")
	
	# If no such file, create one
	if (len(pathToNextCCDNumberList)==0):
		h=open(pathStub + '.0','w')
		h.close()
		return pathStub + '.0'
	else:
		return pathToNextCCDNumberList[0]

#######################################################################################
def getNextCCDScanNumber():
	path = getCCDScanNumberPath()
	return int(path[path.find(".")+1:])

######################################################################################
def incrementCCDScanNumber():
	path = getCCDScanNumberPath()
	nextNumber = int(path[path.find(".")+1:]) + 1
	pathUpToNumber =  path[:path.find(".")+1]
	os.rename(path, pathUpToNumber + str(nextNumber))
	return nextNumber

######################################################################################
def resetCCDScanNumber():
	path = getCCDScanNumberPath()
	pathUpToNumber =  path[:path.find(".")+1]
	os.rename(path, pathUpToNumber + str(0))

def openCCDShield():
	"""
	Ensure ccd shield is open
	"""
	checkConfigured()
	beamline.setValue("Top","-RS-ABSB-07:CON", 0)
	
	# wait and check shield has opened
	sleep(2)
	status = beamline.getValue(None,"Top","-RS-ABSB-07:CON")
	if (status == 0):
		simpleLog("CCD shield opened")
	else:
		simpleLog("CCD shield failed to open - status is: " + status)
		

def closeCCDShield():
	"""
	Ensure ccd shield is closed
	"""
	checkConfigured()
	beamline.setValue("Top","-RS-ABSB-07:CON", 1)
	
	# wait and check shield has closed
	sleep(2)
	status = beamline.getValue(None,"Top","-RS-ABSB-07:CON")
	if (status == 1):
		simpleLog("CCD shield closed")
	else:
		simpleLog("CCD shield failed to close - status is: " + status)
		
######################################################################################
#####
##### The following are some ad-hoc functions written to apply post-processing to 
##### existing images - e.g. applying corrections, correlations, setting detector 
##### distance in file header, etc.
#####
######################################################################################

def ccdProcessDoubles(exposureTime, binning, detectorDistance, fileName, img1Name, img2Name, imageNo="", start=1, end=-1):
	"""
	- Takes 2 darks and correlates. Then for each image: 
		- Imports image files with names (fileRoot + img1Name + suffix) and (fileRoot + img2Name + suffix)
		- Subtracts correlated dark from each image and correlates
		- Inserts detector distance into header of correlated image
		- Exports correlated image

		For example: processDoubles(0.1, 2, 166, "ee863_p03", "_1", "_2")
	"""
	checkConfigured()
	ruby.setBin(binning)
	readOutDelay = 1.5 * ruby.getReadOutDelay()
	importExportDelay = 3*readOutDelay + 5

	#take darks
	totalWait = 2*exposureTime + 3*readOutDelay
	simpleLog("Take darks and wait " + str(totalWait) + " =2*exposure time + 3*export delay")
	ruby.takeDarksAndCorrelate(exposureTime, '1', fileName + '_darks', '1')
	sleep(totalWait)
	
	fileRoot = ruby.path + "/" + fileName
	suffix = str(imageNo) + "_" + str(start)
	dlsRoot = fileRoot.replace("x:/", "/dls/i15/data/")
	fullFileName1 = dlsRoot + img1Name + suffix + ".img"
	fullFileName2 = dlsRoot + img2Name + suffix + ".img"
	
	simpleLog( fullFileName1)
	while ((doesFileExist(fullFileName1) and doesFileExist(fullFileName2)) or start == end):

		totalWait = 2*exposureTime + importExportDelay
		simpleLog("Process double and wait " + str(totalWait) + " =(2*exposure time + import/export delays)")
		cmd = 'call processDouble ' + str(exposureTime) + ' ' + str(binning) + ' ' + str(detectorDistance) + ' "' + fileRoot + '" "' + img1Name + '" "' + img2Name + '" "' + suffix + '"'
		simpleLog(cmd)
		ruby.detector.runScript(cmd)
		sleep(totalWait)

		start = start + 1
		suffix = str(imageNo) + "_" + str(start) 
		fullFileName1 = dlsRoot + img1Name + suffix + ".img"
		fullFileName2 = dlsRoot + img2Name + suffix + ".img"
	
	simpleLog("----- Script ended ------")

#########################################################
def ccdApplyCorrections(folder, detectorDistance):
	"""
	For each .img file in folder, runs ruby.importAndCorrect(...) 3 times, with corrections to apply
	set to (floodm), (floodm, unwarp) and (floodm, unwarp, floodp). This imports the file into
	IS, applies the relevant corrections and exports the file (with suffix '_correction1', '_correction2'
	or '_correction3' .

	e.g. ccdApplyCorrections("/dls/i15/data/2008/ee863-1/Silicon", 142)
	ccdApplyCorrections("/dls/i15/data/testsDec18", 142)
	"""
	checkConfigured()
	ruby.setDetectorDist(detectorDistance)
	ruby.setFloodFile("lib/bin/crysalis/floodmo_ruby_6_120905.ffiinf")

	ruby.applyCorr("repair")
	corrsToApply = ["floodm", "unwarp", "floodp"]
	for corr in corrsToApply:
		ruby.removeCorr(corr)

	sleep(2)
	simpleLog("\n\n ====Start processing====\n")
	fileList = glob.glob(folder + "/*")
	for i in range(0, len(corrsToApply), 1):
		ruby.applyCorr(corrsToApply[i])
		for f in fileList:
			if (f.endswith(".img")):
				simpleLog("--> " + str(f))
				fileWIthoutExt = f.replace(".img", "")
				fileWIthoutExt = fileWIthoutExt.replace("/dls/i15/data", "X:")
				#simpleLog("ruby.import... " + fileWIthoutExt + " corr: " + `i+1`)
				ruby.importAndCorrect(fileWIthoutExt, "_correction" + str(i + 1))
				simpleLog("Wait 20s to ensure files imported and exported")
				simpleLog("")
				simpleLog("")
				sleep(20)

	simpleLog("\n\n ====Finished====\n")
	
def ccdApplyCorrections2(folder, corrsToApply, detectorDistance):
	"""
	For each .img file in folder, apply corrections corrsToApply and run ruby.importAndCorrect2(...). This imports the file into
	IS, sets detector distance, applies the relevant corrections and exports the file.

	e.g. ccdApplyCorrections2("/dls/i15/data/2008/ee863-1/garnet/", ["repair", "floodm", "unwarp", "floodp"], 142)
	ccdApplyCorrections2("/dls/i15/data/testsDec18/test/", ["repair", "floodm", "unwarp", "floodp"], 142)
	"""
	checkConfigured()
	ruby.setDetectorDist(detectorDistance)
	ruby.setFloodFile("lib/bin/crysalis/floodmo_ruby_6_120905.ffiinf")
	
	for i in range(0, len(corrsToApply), 1):
		ruby.applyCorr(corrsToApply[i])
		
	sleep(2)
	simpleLog("\n\n ====Start processing====\n")
	fileList = glob.glob(folder + "/*")

	folderX = folder.replace("/dls/i15/", "X:")
	
	totalNoOfFiles = len(fileList)
	simpleLog("No of files: " + str(totalNoOfFiles))
	fileNo = 1
	for filePath in fileList:
		if (filePath.endswith(".img") and not filePath.__contains__("molycorrected")):
			simpleLog("--> " + str(fileNo) + "of " + str(totalNoOfFiles) +": " + str(filePath))
			fileName = filePath.replace(folder, "")
			underscoreIndex = fileName.find("_")
			correctedFileName = fileName[:underscoreIndex] + "_molycorrected" + fileName[underscoreIndex:]
			if (not doesFileExist(folder + correctedFileName)):
				cmd = 'call importAndCorrect2  "' + folderX + '" "' + fileName + '" ' + ruby.getCorrectionsString() + ' ' + str(ruby.detectorDistance) + ' "' + correctedFileName + '"'
				simpleLog ("IS command: " + cmd )
				ruby.detector.runScript(cmd)
				
				simpleLog("")
				simpleLog("")
				
				fileExported = checkFileExistsWithTimeout(folder, correctedFileName, 20)
				if (not fileExported):
					simpleLog("Problem exporting file: " + folder + correctedFileName)
				fileNo = fileNo + 1
				#break

	simpleLog("\n\n ====Finished====\n")

#############
def checkFileExistsWithTimeout(folder, f, timeout):
	"""
	Returns true if file exists within the given timeout.
	"""
	checkConfigured()
	t0 = time.clock()
	t1 = t0
	while ( (t1 - t0) < timeout ): 
		os.system("ls " + folder)     # forces folder to be updated on dls system
		if (doesFileExist(folder + f)):
			return True
		t1 = time.clock()
		pause()                     # ensures script can be stopped promptly

	return False
