import sys;
import string;
import handle_messages;
import gda.factory.Finder as Finder;
import BeamlineParameters;
import java
from time import sleep
from gda.device.epicsdevice import ReturnType
from gda.px.util import VisitPath
from gda.analysis import ScanFileHolder
import gda
def checkOE(jythonNameMap, oeName, expectedDOFNames):
	ok = True
	try:
		oe = jythonNameMap.__getattr__(oeName)
		print oe
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

def checkOEs(command_server):
	#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
	jythonNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())
	print jythonNameMap
	ok = True
	ok = checkOE(jythonNameMap,"Dummy", ['dummyaxis'])  and ok
	print 'checking dummymotor ', ok
	ok = checkOE(jythonNameMap,"ID", ['idgap']) and ok
	print'checking id', ok
	ok = checkOE(jythonNameMap,"D1", ['d1motor']) and ok
	print 'checking d1 ' ,ok
	ok = checkOE(jythonNameMap,"D2", ['d2motor']) and ok
	ok = checkOE(jythonNameMap,"D3", ['d3motor']) and ok
	ok = checkOE(jythonNameMap,"D5", ['d5amotor', 'd5bmotor']) and ok
	ok = checkOE(jythonNameMap,"D6", ['d6amotor', 'd6bmotor']) and ok
	ok = checkOE(jythonNameMap,"D7", ['d7amotor', 'd7bmotor']) and ok
	ok = checkOE(jythonNameMap,"S1", ['s1xgap', 's1xpos', 's1ygap', 's1ypos']) and  ok
	ok = checkOE(jythonNameMap,"Toroid", ['toroid_sag', 'toroid_pitch', 'toroid_x', 'toroid_roll', 'toroid_curve', 'toroid_ellipticity', 'toroid_y', 'toroid_yaw']) and ok
	ok = checkOE(jythonNameMap,"DCM", ["dcm_bragg", "dcm_crystal1_roll", "dcm_crystal2_roll", "dcm_crystal2_pitch", "dcm_perp", "dcm_mono"] ) and  ok
	ok = checkOE(jythonNameMap,"S2", ['s2xgap', 's2xpos', 's2ygap', 's2ypos']) and  ok
	ok = checkOE(jythonNameMap,"S3", ['s3xgap', 's3xpos', 's3ygap', 's3ypos', 's3xminus', 's3xplus', 's3yplus', 's3yminus']) and  ok
	ok = checkOE(jythonNameMap,"KB", ['kb_vfm_y', 'kb_vfm_x', 'kb_vfm_pitch', 'kb_hfm_x', 'kb_hfm_y', 'kb_hfm_pitch']) and ok
	ok = checkOE(jythonNameMap,"PinHole", ['pinx', 'piny']) and ok
	ok = checkOE(jythonNameMap,"TungstenWire", ['TungstenWireY']) and ok
	ok = checkOE(jythonNameMap,"MicroFocusSampleStage", ['sample_z', 'sample_thetacoarse', 'MicrofocusSampleX', 'sample_y1', 'sample_y2', 'sample_y3', 'sample_thetafine', 'MicroFocusSampleY']) and ok
	ok = checkOE(jythonNameMap,"VMA", ['vma_zoom', 'vma_focus']) and ok
	#ok = checkOE(jythonNameMap,"CCD", ['ccdx', 'ccdy']) and ok
	ok = checkOE(jythonNameMap,"MultiLayer", [ 'm1_x', 'm1_y', 'm1_z', 'm1_angle', 'm1_screen', 'm1_det']) and ok
	#ok = checkOE(jythonNameMap,"WDS", ['wds_x', 'wds_y', 'wds_z']) and ok
	ok = checkOE(jythonNameMap,"HR", ['hrm_combined_x', 'hrm_combined_pitch', 'hrm_shr_x']) and ok
	ok = checkOE(jythonNameMap,"ComboDCMController", ['comboDCM_d', 'comboDCM_nogap']) and ok
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

def checkAdcs(command_server):
	finderNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())
	
	ok = True
	ok = checkAdc(finderNameMap,"ip330a") and ok
	ok = checkAdc(finderNameMap,"ip330b") and ok
	return ok

def checkCounterTimer(jythonNameMap, name, expectedReadoutSize):
	ok = True
	try:
		obj = jythonNameMap.__getattr__(name)
		obj.setCollectionTime(1.0)
		obj.collectData()
		data = obj.readout()
		print data[0]
		if isinstance( obj , gda.device.detector.countertimer.EpicsMCACounterTimer):
			length = len( data[0][0] )
		else:
			length = len( data )
		if( length  != expectedReadoutSize):
			raise "Error - readoutSize = " + `expectedReadoutSize` + " "+ `length`
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking counterTimer  " + name, type, exception, None, False)
		ok = False
	return ok

def checkCounterTimers(command_server):
	#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
	jythonNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())
	ok = True
	ok = checkCounterTimer(jythonNameMap,"counterTimer01", 4) and ok
	ok = checkCounterTimer(jythonNameMap,"counterTimer02", 9) and ok
	ok = checkCounterTimer(jythonNameMap,"counterTimer03", 3) and ok
	return ok

def checkAnalyser(finderNameMap, name):
	ok = True
	try:
		obj = finderNameMap.__getattr__(name)
		if isinstance( obj, gda.device.EpicsTca): 
			obj.getAttribute("SCA1HI")
			obj.getAttribute("energyToChannel10000 eV")
		elif isinstance(obj, gda.device.detector.analyser.EpicsMCA):
			print obj.getNumberOfRegions()
			print (obj.getPresets()).presetLiveTime
			##obj.getAttribute("energyToChannel10000 eV")
			print obj.getStatus()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking analyser  " + name, type, exception, None, False)
		ok = False
	return ok

def checkAnalysers(command_server):
	#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
	finderNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())	
	ok = True
	ok = checkAnalyser(finderNameMap,"ionchamber1") and ok
	ok = checkAnalyser(finderNameMap,"ionchamber2") and ok
	ok = checkAnalyser(finderNameMap,"draincurrent") and ok
	return ok

def checkXspress(command_server,name):
	ok = True
	#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
	finderNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())
	try:
		obj=finderNameMap.__getattr__(name)
		data=obj.readout()    
		print data    
		if(data == None):
			raise "Error - xspress readout  " 
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking analyser  " + name, type, exception, None, False)
		ok = False
	return ok
#not used
def checkCCD(name):
	ok = True
	try:
		
		obj = finderNameMap.__getattr__(name)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"Error checking analyser  " + name, type, exception, None, False)
		ok = False
	return ok

	
#for future use
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

def checkCameras(command_server):
	finderNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())
	jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)	
	ok = True
	#ok = checkCamera(finderNameMap,jythonNameMap,"PXCamera" ) and ok
	return ok


#for future use
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

def checkFileHeaders(command_server):
	finderNameMap = BeamlineParameters.FinderNameMapping(Finder.getInstance())
	jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)	
	ok = True
	#ok = checkFileHeader(finderNameMap,jythonNameMap,"PXFileHeader" ) and ok
	return ok

def checkAutomaticHarmonicChange(name):
	pass
def checkExafsFluScan(command_server):
	ok = True
	try:
		#Mn_Ka	[528,596]	[576,644]	[544,616]	[505,576]	[540,652]	[509,588]	[548,628]	[536,620]	[477,576]
		toComparefile = '/dls/i18/data/2009/sp870-1/29745.dat'
		jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
		#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
		#myscan=I18ExafsScanClass()
		#myscan.setWindows('/dls/i18/software/gda/config/var/windows/Mn_Ka.cnf','Mn_Ka')
		#myscan.setHeaderInfo('','','','')
		#myscan.setNoOfRepeats(1)
		#myscan.addAngleScan(18031.6,17659.6,-16.16086956521742,1000.0)
		#myscan.addAngleScan(17659.600000000002,17508.4,-2.8000000000000136,1000.0)
		#myscan.addKScan(3.0,12.0,0.04,1000.0,9000.0,3,6.53752627125262,6.271000000000002)
		#myscan.startScan()
		
		#check data file
		#print myscan.getDataFileName()
		#scanfile=myscan.getDataFileName()
		scanfile='/dls/i18/data/2009/sp0/33035.dat'
		compareColumns=readScanFile(toComparefile)
		scanColumns=readScanFile(scanfile)
	
		for i in range(3):
			try:
				compareColumnValues(compareColumns[i], scanColumns[i])
				
			except:
				print 'error in comparing the column number ' + str(i)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkExafsFluScan - error ", type, exception, None, False)
				ok = False
		
		print 'comparing ion chamber columns 4 -6'
		for j in range(3,6,1):
			try:
				compareColumnsinRange(compareColumns[j], scanColumns[j])
			except:
				print 'error in comparing ion chamber values column number '+ str(j)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkExafsFluScan - error ", type, exception, None, False)
				ok = False
	
		print 'comparing the detector columns 8 -16'
		for k in range(6,16,1):
			try:
				compareColumnMean(compareColumns[k], scanColumns[k])
		#del myscan
			except:
				print 'error in comparing detector columns number ' + str(k)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkExafsFluScan - error ", type, exception, None, False)
				ok = False
		##compare the mca files
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkExafsFluScan - error ", type, exception, None, False)
		ok = False
		#del myscan
	return ok

def checkExafsTransScan(command_server):
	ok = True
	try:
		toComparefile = '/dls/i18/data/2009/sp870-1/29757.dat'
		#Mn_Ka	[528,596]	[576,644]	[544,616]	[505,576]	[540,652]	[509,588]	[548,628]	[536,620]	[477,576]
		jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
		myscan=I18TransmissionExafsScanClass()
		myscan.setWindows('/dls/i18/software/gda/config/var/windows/Mn_Ka.cnf','Mn_Ka')
		myscan.setHeaderInfo('','','','')
		myscan.setNoOfRepeats(1)
		myscan.addAngleScan(18031.6,17659.6,-16.16086956521742,1000.0)
		myscan.addAngleScan(17659.600000000002,17508.4,-2.8000000000000136,1000.0)
		myscan.addKScan(3.0,12.0,0.04,1000.0,9000.0,3,6.53752627125262,6.271000000000002)
		myscan.startScan()		
		#print myscan.getDataFileName()
		scanfile=myscan.getDataFileName()
		#scanfile='/dls/i18/data/2009/sp0/33049.dat'
		compareColumns=readScanFile(toComparefile)
		scanColumns=readScanFile(scanfile)
		for i in range(3):
			try:
				compareColumnValues(compareColumns[i], scanColumns[i])
			except:
				print 'error in comparing the column number ' + str(i)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkExafsTransScan - error ", type, exception, None, False)
				ok = False
		print 'comparing ion chamber columns 4 -6'
		for j in range(3,6,1):
			try:
				compareColumnsinRange(compareColumns[j], scanColumns[j])
			except:
				print 'error in comparing the column number ' + str(j)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkExafsTransScan - error ", type, exception, None, False)
				ok = False
		
		del myscan
		
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkExafsTransScan - error ", type, exception, None, False)
		ok = False
	
	return ok


def checkStepFluScan(command_server):
	ok = True
	try:
		#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
		#Mn_Ka	[528,596]	[576,644]	[544,616]	[505,576]	[540,652]	[509,588]	[548,628]	[536,620]	[477,576]
		#Mn_Kb	[604,644]	[648,707]	[612,676]	[576,632]	[640,691]	[592,632]	[628,672]	[624,676]	[572,624]
		toComparefile = 'dls/i18/data/2009/sp870-1/29747.dat'
		myscan=I18StepMapClass()
		myscan.stepmapscan(0.0,0.3,0.01,0.0,0.3,0.01,1000.0)
		print myscan.getDataFileName()
		##check data file
		scanfile=myscan.getDataFileName()
		compareColumns=readScanFile(toComparefile,3)
		scanColumns=readScanFile(scanfile,3)
		for i in range(3):
			try:
				compareColumnValues(compareColumns[i], scanColumns[i])
			except:
				print 'error in comparing the column number ' + str(i)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkStepFluScan - error ", type, exception, None, False)
				ok = False
		print 'comparing ion chamber columns 4 -6'
		for j in range(3,6,1):
			try:
				compareColumnsinRange(compareColumns[j], scanColumns[j])
			except:
				print 'error in comparing the column number ' + str(i)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkStepFluScan - error ", type, exception, None, False)
				ok = False
		##compare the mca files
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkStepFluScan - error ", type, exception, None, False)
		ok = False
	return ok

def checkStepTransScan(command_server):
	ok = True
	try:
		toComparefile = 'dls/i18/data/2009/sp870-1/29759.dat'
		#Mn_Ka	[528,596]	[576,644]	[544,616]	[505,576]	[540,652]	[509,588]	[548,628]	[536,620]	[477,576]
		#Mn_Kb	[604,644]	[648,707]	[612,676]	[576,632]	[640,691]	[592,632]	[628,672]	[624,676]	[572,624]
		myscan=I18TransmissionMapClass()
		myscan.stepmapscan(0.0,0.3,0.01,0.0,0.3,0.01,1000.0)
		#jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)
		#check data file
		scanfile=myscan.getDataFileName()
		compareColumns=readScanFile(toComparefile,3)
		scanColumns=readScanFile(scanfile,3)
		for i in range(3):
			try:
				compareColumnValues(compareColumns[i], scanColumns[i])
			except:
				print 'error in comparing the column number ' + str(i)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkStepTransScan - error ", type, exception, None, False)
				ok = False
		print 'comparing ion chamber columns 4 -6'
		for j in range(3,6,1):
			try:
				compareColumnsinRange(compareColumns[j], scanColumns[j])
			except:
				print 'error in comparing the column number ' + str(i)
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None,"checkStepTransScan - error ", type, exception, None, False)
				ok = False
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkStepTransScan - error ", type, exception, None, False)
		ok = False
	return ok
##not used
def checkContinuousScan(command_server):
	ok = True
	try:
		I18ContinuousScanClass.setupGUI()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkScan1 - error ", type, exception, None, False)
		ok = False
	return ok
##for future use
def checkScannable(jythonNameMap, obj):
	ok = True
	try:
		obj.getPosition()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None,"checkScannable - error " + obj.getName(), type, exception, None, False)
		ok = False
	return ok

def checkScannables(command_server):
	ok = True
	numScannables=0
	jythonNameMap = BeamlineParameters.JythonNameSpaceMapping(command_server)	
	finder = Finder.getInstance()
	allObjectNamesString = command_server.evaluateCommand("dir()")
	allObjectNames = allObjectNamesString.split(",")
	for objectName in allObjectNames:
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
			handle_messages.log(None,"checkScannables - error getting attribute " + objectName, type, exception, None, False)
			ok = False
	if(numScannables != 113):
		print "Error number of Scannable != 113. Actual number = " + `numScannables`
		ok = False
	return ok

def checkAll():
	ok = True
	command_server = Finder.getInstance().find("command_server")
	#ok = checkExafsFluScan(command_server) and ok
	ok = checkExafsTransScan(command_server) and ok
	#ok = checkStepFluScan(command_server) and ok
	#ok = checkStepTransScan(command_server) and ok
	#ok = checkXspress(command_server) and ok
	#ok = checkAnalysers(command_server) and ok
	#ok = checkCounterTimers(command_server) and ok
	#ok = checkAdcs(command_server) and ok
	#ok = checkOEs(command_server) and ok
	#ok = LookupTables.reloadLookupTablesEx(False) and ok
	if( not ok):
		print "checkAll completed with error"
	return ok

def readScanFile(filename, linestoskip=7):
	fid=open(filename)
	lines=fid.read()
	fid.close()
	lines=lines.split('\n')
	lines= lines[linestoskip:len(lines)-1]
	print lines
	length= len(lines)
	rows=[]
	columns=[]
	print length
	for i in range(length):
		#print i
		rows.append(lines[i].split())
		#print rows[i]
	##transposing the rows and columns
	columns =map(list, zip(*rows))
	#print columns
	return columns
    
    #print lines
def compareColumnsinRange(column1, column2):
	if (len(column1) != len(column2)) :
		raise 'Error columns are not of  the same length '+ str(len(column1[i])) + " "+str(len(column2[i]))
	acceptableDiff= float(column1[0]) * 0.05
	ok = True
	for i in range(len(column1)):
		if(float(column1[i]) < 0.0 or float(column2[i]) < 0.0):
			raise  " Error columns have negative values, "+column1[i]+" "+ column2[i]
		if(abs(float(column1[i]) - float(column2[i])) <= acceptableDiff):
			#print column1[i], " ", column2[i]
			continue
		else:
			 raise "Error - column values are not with the acceptable five percent range in line number , " +str(i) +" "+column1[i]+" "+ column2[i]
	return ok
def compareColumnValues(column1, column2):
	print len(column1), len(column2)
	if (len(column1) != len(column2)) :
		raise 'Error columns are not of  the same length '+ str(len(column1[i])) + " "+str(len(column2[i]))
	
	ok = True
	for i in range(len(column1)):
	#	print column1[i], column2[i]
		if(float(column1[i]) < 0.0 or float(column2[i]) < 0.0):
			#print 'negative error 1'
			raise  " Error columns have negative values in line number , " + str(i) +" " +column1[i]+" "+ column2[i]
		
		if(float(column1[i]) == float(column2[i])):
			#print 'equal'
			continue
		else:
			#print 'not equal'
			raise "Error - column values are not equal in line number , " + str(i) +" "+column1[i]+" "+ column2[i]
	return ok
def compareColumnMean(column1, column2):
	if (len(column1) != len(column2)) :
		raise 'Error columns are not of  the same length '+ str(len(column1[i])) + " "+str(len(column2[i]))
	
	ok = True
	column1Tot=0.0
	column2Tot =0.0
	l = float(len(column1))
	for i in range(len(column1)):
		if(float(column1[i]) < 0.0 or float(column2[i]) < 0.0):
			raise  " Error columns have negative values in line number , " + str(i) +" "+column1[i]+" "+ column2[i]
	#	print column1[i], " ", column2[i]
		column1Tot += float(column1[i])
		column2Tot += float(column2[i])
	column1Mean=column1Tot / l
	column2Mean=column2Tot / l
	acceptableDiff = column1Mean * 0.05
	if(abs(column1Mean - column2Mean) <= acceptableDiff):
		return ok
	else:
		raise "Error - column mean value is not equal in line number , " + str(i) +" "+ str(column1Mean)+ " "+ str(column2Mean) 
	return ok
