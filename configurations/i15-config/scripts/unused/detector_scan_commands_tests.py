import gda
import gdascripts
import java
import junitx
import os.path
import random
import re
import shutil
import sys
import unittest
import dummy_detector_wrappers
import detector_scan_commands

from gda.configuration.properties import LocalProperties
from gda.analysis import ScanFileHolder
from gda.data import NumTracker
from ch.qos.logback.classic.joran import JoranConfigurator
from gda import TestHelpers
from gda.configuration.properties import LocalProperties
from gda.jython import InterfaceProvider, MockJythonServerFacade, MockJythonServer
from org.slf4j import LoggerFactory
from java.io import File, FileNotFoundException, ByteArrayInputStream

from gda.scan import ConcurrentScan

class ScanCommandsTests(unittest.TestCase):
	def idOfTest(self):
		return self.id().replace("__main__","ScanCommandsTests")
	
	def getActualOutputPath(self):
	    return "/dls/i15/software/gda_versions/gda_7_14/i15-config/scripts/i15tests/" + self.idOfTest()
	   
	def getExpectedOutputPath(self):
		return TestFileFolder + self.idOfTest()

	def setUp(self):
		outputPath = self.getActualOutputPath()
		TestHelpers.makeScratchDirectory(outputPath)
		
		loggerContext = LoggerFactory.getILoggerFactory();
		joranConfigurator  =  JoranConfigurator();
		loggerContext.shutdownAndReset();
		joranConfigurator.setContext(loggerContext);
		f = '<?xml version="1.0" encoding="UTF-8"?>' + \
			'<configuration>' + \
				'<appender name="DebugFILE" class="ch.qos.logback.core.FileAppender">' + \
						'<File>' +  outputPath +"/log.txt" + '</File>'+ \
						'<layout class="ch.qos.logback.classic.PatternLayout">' + \
							'<pattern>%d %-5level [%property{GDA_SOURCE}/%property{JVMNAME}] %logger - %m%n%rEx</pattern>' + \
						'</layout>' + \
					'</appender>' + \
				'<logger name="gda"><level value="DEBUG"/></logger>' + \
				'<root><level value="ALL"/><appender-ref ref="DebugFILE"/></root>' + \
			'</configuration>'
		joranConfigurator.doConfigure(ByteArrayInputStream(java.lang.String(f).getBytes()))

		mockJythonServerFacade = MockJythonServerFacade()
		mockJythonServer = MockJythonServer()
		InterfaceProvider.setCommandRunnerForTesting(mockJythonServerFacade)
		InterfaceProvider.setCurrentScanControllerForTesting(mockJythonServerFacade)
		InterfaceProvider.setTerminalPrinterForTesting(mockJythonServerFacade)
		InterfaceProvider.setScanStatusHolderForTesting(mockJythonServerFacade)
		InterfaceProvider.setJythonNamespaceForTesting(mockJythonServerFacade)
		InterfaceProvider.setCurrentScanHolderForTesting(mockJythonServer)
		InterfaceProvider.setJythonServerNotiferForTesting(mockJythonServer)
		InterfaceProvider.setDefaultScannableProviderForTesting(mockJythonServer)
		InterfaceProvider.setAuthorisationHolderForTesting(mockJythonServerFacade)
		InterfaceProvider.setScanDataPointProviderForTesting(mockJythonServerFacade)
		#LocalProperties.set("gda.data.numtracker", "/dls/i15/software/gda_versions/gda_7_14/i15-config/var/")
		LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/i15/data/2009/0-0/")
		LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")
		
	def doesFileExist(self, f):
		try:
			file=open(f)
		except IOError:
			exists = False
		else:
			exists = True
		return exists
	
	def checkImagesWritten(self):
		tracker = NumTracker("tmp")
		scanNumber = tracker.getCurrentFileNumber()
		
		fileDir = LocalProperties.get("gda.data.scan.datawriter.datadir")
		dataFileLocation = fileDir + str(scanNumber) + ".dat"
		f = open(dataFileLocation, 'r')
		
		fileContent = f.read()
		endIndex = fileContent.find("&END")
		fileContent = fileContent[endIndex:]
		
		imageFileName = "dummyPilatus"
		lines = fileContent.strip().split("\n")
		
		for line in lines[2:]:
			fileNameStart=line.index(fileDir)
			files = line[fileNameStart:-1]
			files=files.split(",")
			for file in files:
				file = file.replace("'","").strip()
				fileExists = self.doesFileExist(file)
				self.assertEquals(fileExists, True)
				#print "File: ", file, " Exists = ", fileExists
	
	def scanDummyWrapper(self, detectorType, start, stop, step, exposureTime, noOfExpPerPos):
	
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		axis = dummy_detector_wrappers.DummyMotor()
		sync = False
		
		if detectorType == "pilatus":
			detector = None
			fileName = "dummyPilatusTest"
			wrappedDetector = dummy_detector_wrappers.DummyPilatusWrapper(detector, exposureTime, axis, step, sync, fileName, noOfExpPerPos)
		if detectorType == "mar":
			detector = None
			fileName = "dummyMarTest"
			wrappedDetector = dummy_detector_wrappers.DummyMarWrapper(detector, exposureTime, axis, step, sync, fileName, noOfExpPerPos)
		if detectorType == "ruby":
			detector = None
			fileName = "dummyRubyTest"
			wrappedDetector = dummy_detector_wrappers.DummyRubyWrapper(detector, exposureTime, axis, step, sync, fileName, noOfExpPerPos)
		if detectorType == "atlas":
			detector = None
			fileName = "dummyAtlasTest"
			wrappedDetector = dummy_detector_wrappers.DummyAtlasWrapper(detector, exposureTime, axis, step, sync, fileName, noOfExpPerPos)
			
		scan = ConcurrentScan([wrappedDetector, start, stop, step])
		scan.runScan()
		
		self.checkImagesWritten()
	
	
	#ant -file /home/zhb16119/gdaWorkspace/uk.ac.gda.core/build-classic.xml -Djython.file=/home/zhb16119/gdaWorkspace/gda-config-base/scripts/detector_scan_commands_tests.py -Dpython.path=scripts jyunit_run_script
	def testDummyWrappers(self):
		pass
		#self.scanDummyWrapper("pilatus", 0., 5., 1., 1, 3)
		#self.scanDummyWrapper("mar", 0., 5., 1., 1, 3)
		#self.scanDummyWrapper("ruby", 0., 5., 1., 1, 3)
		
	def testSimpleScan(self):
		
		
		
		from gdascripts.parameters import beamline_parameters
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		pilatus = jythonNameMap.__getattr__("pilatus")
		print dir(pilatus)
		#axis = jythonNameMap.dkphi
		#start = 0.
		#stop = 5.
		#step = 1.
		
		#import pd_pilatus
		#detector = pd_pilatus.Pilatus("pilatus","BL15I-EA-PILAT-02:","/dls/i15/data/currentdir/", "pil")
		
		#exposureTime = 1
		#noOfExpPerPos = 1.
		#fileName = "automatedPilatusTest"
		#detector_scan_commands.simpleScan(axis, start, stop, step, detector, exposureTime, noOfExpPerPos, fileName)
		#self.checkImagesWritten()
		
		# Tests will use dkphi for the axis. Detectors can be pilatus, ruby, or mar.
		
		# simpleScan tests
		# Usage: simpleScan(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=1, fileName="scan_test")
		
		# simple scan test 1 - Scan from 0 to 5 with step size of 1 exposing the pilatus for 1 second at each step
		# Test that the filenames are written correctly and that the axis has moved correctly for varying parameters
		
		# Test No. |  axis  | start | stop | step | detector | exposureTime | noOfExpPerPos |		 fileName
		#----------------------------------------------------------------------------------------------------------------
		#	 1	| dkphi  |   0   |  5   |   1  | pilatus  |	   1	  |		1	  |  pilatus_simple_scan_test
		#	 2	| dkphi  |   0   |  5   |   1  | pilatus  |	   1	  |		10	  |  pilatus_simple_scan_test
		#	 3	| dkphi  |   0   |  5   |   1  | pilatus  |	   10	  |		1	  |  pilatus_simple_scan_test
		#	 4	| dkphi  |   -5  |  5   |   2  | pilatus  |	   1	  |		1	  |  pilatus_simple_scan_test
		#	 5	| dkphi  |   0   |  5   |   1  |   mar	  |	   1	  |		1	  |  mar_simple_scan_test
		#	 6	| dkphi  |   0   |  5   |   1  |   mar	  |	   1	  |		10	  |  mar_simple_scan_test
		#	 7	| dkphi  |   0   |  5   |   1  |   mar	  |	   10	  |		1	  |  mar_simple_scan_test
		#	 8	| dkphi  |   -5  |  5   |   2  |   mar	  |	   1	  |		1	  |  mar_simple_scan_test

	#def testSimpleScanUnsync(self):
		
		# simpleScanUnsync tests
		# Usage: simpleScanUnsync(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=1, fileName="scan_test")
		
		# Test No. |  axis  | start | stop | step | detector | exposureTime | noOfExpPerPos |		 fileName
		#----------------------------------------------------------------------------------------------------------------
		#	 1	| dkphi  |   0   |  5   |   1  | pilatus  |	   1	  |		1	  |  pilatus_simple_scan_unsync_test
		#	 2	| dkphi  |   0   |  5   |   1  | pilatus  |	   1	  |		10	 |  pilatus_simple_scan_unsync_test
		#	 3	| dkphi  |   0   |  5   |   1  | pilatus  |	   10	 |		1	  |  pilatus_simple_scan_unsync_test
		#	 4	| dkphi  |   -5  |  5   |   2  | pilatus  |	   1	  |		1	  |  pilatus_simple_scan_unsync_test
		#	 5	| dkphi  |   0   |  5   |   1  |   mar	  |	   1	  |		1	  |  mar_simple_scan_unsync_test
		#	 6	| dkphi  |   0   |  5   |   1  |   mar	 |	   1	  |		10	 |  mar_simple_scan_unsync_test
		#	 7	| dkphi  |   0   |  5   |   1  |   mar	|	   10	 |		1	  |  mar_simple_scan_unsync_test
		#	 8	| dkphi  |   -5  |  5   |   2  |   mar	|	   1	  |		1	  |  mar_simple_scan_unsync_test
		
	#def testrockScan(self):
				
		# rockScan tests
		# Usage: rockScan(axis, centre, rockSize, noOfRocks, detector, exposureTime, fileName="rock_scan_test")
		
		# Test No. |  axis  | centre | rockSize | noOfRocks | detector | exposureTime |		 fileName
		#----------------------------------------------------------------------------------------------------------------
		#	 1	| dkphi  |   0	|	1	 |	 1	 | pilatus  |	   1	  | pilatus_rock_scan_test	
		#	 2	| dkphi  |   0	|	5	 |	 1	 | pilatus  |	   1	  | pilatus_rock_scan_test	
		#	 3	| dkphi  |   0	|	1	 |	 5	 | pilatus  |	   1	  | pilatus_rock_scan_test	
		#	 4	| dkphi  |   0	|	1	 |	 1	 | pilatus  |	   5	  | pilatus_rock_scan_test	
		#	 5	| dkphi  |   0	|	1	 |	 1	 |   mar	|	   1	  | mar_rock_scan_test	
		#	 6	| dkphi  |   0	|	5	 |	 1	 |   mar	|	   1	  | mar_rock_scan_test	
		#	 7	| dkphi  |   0	|	1	 |	 5	 |   mar	|	   1	  | mar_rock_scan_test	
		#	 8	| dkphi  |   0	|	1	 |	 1	 |   mar	|	   5	  | mar_rock_scan_test	
		
	#def testrockScanUnsync(self):
		
				
		# rockScanUnsync tests
		# Usage: rockScanUnsync(axis, centre, rockSize, noOfRocks, detector, exposureTime, fileName="rock_scan_test")
		
		# Test No. |  axis  | centre | rockSize | noOfRocks | detector | exposureTime |		 fileName
		#----------------------------------------------------------------------------------------------------------------
		#	 1	| dkphi  |   0	|	1	 |	 1	 | pilatus  |	   1	  | pilatus_rock_scan_unsync_test	
		#	 2	| dkphi  |   0	|	5	 |	 1	 | pilatus  |	   1	  | pilatus_rock_scan_unsync_test	
		#	 3	| dkphi  |   0	|	1	 |	 5	 | pilatus  |	   1	  | pilatus_rock_scan_unsync_test	
		#	 4	| dkphi  |   0	|	1	 |	 1	 | pilatus  |	   5	  | pilatus_rock_scan_unsync_test	
		#	 5	| dkphi  |   0	|	1	 |	 1	 |   mar	|	   1	  | mar_rock_scan_unsync_test	
		#	 6	| dkphi  |   0	|	5	 |	 1	 |   mar	|	   1	  | mar_rock_scan_unsync_test	
		#	 7	| dkphi  |   0	|	1	 |	 5	 |   mar	|	   1	  | mar_rock_scan_unsync_test	
		#	 8	| dkphi  |   0	|	1	 |	 1	 |   mar	|	   5	  | mar_rock_scan_unsync_test	
		
	#def testExpose(self):
		
	
		# expose tests
		# Usage: expose(detector, exposureTime=1, noOfExposures=1, fileName="expose_test")
		
		# Test No. | detector | exposureTime | noOfExposures |		 fileName
		#----------------------------------------------------------------------------
		#	 1	| pilatus  |	  1	   |	   1	   | pilatus_expose_test	
		#	 2	| pilatus  |	  1	   |	   5	   | pilatus_expose_test	
		#	 3	| pilatus  |	  5	   |	   1	   | pilatus_expose_test	
		#	 4	|   mar	   |	  1	   |	   1	   | mar_expose_test	
		#	 5	|   mar	   |	  1	   |	   5	   | mar_expose_test	
		#	 6	|   mar	   |	  5	   |	   1	   | mar_expose_test
		
	#def testDarkExpose(self):
		
		# darkExpose tests
		# Usage: darkExpose(detector, exposureTime=1, noOfExposures=1, fileName="dark_expose_test")
		
		# Test No. | detector | exposureTime | noOfExposures |		 fileName
		#-------------------------------------------------------exafsTest---------------------
		#	 1	| pilatus  |	  1	   |	   1	   | pilatus_dark_expose_test	
		#	 2	| pilatus  |	  1	   |	   5	   | pilatus_dark_expose_test	
		#	 3	| pilatus  |	  5	   |	   1	   | pilatus_dark_expose_test	
		#	 4	|   mar	   |	  1	   |	   1	   | mar_dark_expose_test	
		#	 5	|   mar	   |	  1	   |	   5	   | mar_dark_expose_test	
		#	 6	|   mar	   |	  5	   |	   1	   | mar_dark_expose_test	


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(ScanCommandsTests)	  
if __name__ == '__main__':
	unittest.TextTestRunner(verbosity=2).run(suite())
