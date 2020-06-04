
from gda.device.detector import DetectorBase
from gda.device import Detector

class ExcaliburOdinDetectorClass(DetectorBase):
	#DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);

	def __init__(self, name):
		self.setName(name)
		self.setInputNames([name])
		self.setExtraNames([])
		self.setLevel(7)

		self.scanNumberTracker = NumTracker("tmp")

		self.fileName=None
		#self.data = ScanFileHolder()
		self.exposureTime = 0

		self.logScale = False
		self.alive=True

#		To setup the image folder according to I06 requirement
		self.scanImageDirectory()
		self.fastMode=False
		self.protection=True

		self.verbose = False

	#DetectorBase Impl
	def getPosition(self):
		return self.readout()

	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos)
		self.collectData()

	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime()
		return self.exposureTime

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos
		self.detector.setCollectionTime(self.exposureTime)

	def collectData(self):
		#self.detector.setCollectionTime(self.exposureTime)
		self.detector.collectData()
		return

	def prepareForCollection(self):
		#To put camera in the "camera mode"
		self.detector.setCameraInProgress(False)
		self.detector.prepareForCollection()

	def endCollection(self):
#		self.detector.endCollection()
		if self.protection:
			self.protectCamera()
		return

	def readout(self):
		self.fileName  = self.detector.readout()
		if self.alive:
			self.display()
		return self.fileName

	def getStatus(self):
		return self.detector.getStatus()

	def createsOwnFiles(self):
		return True

	def toString(self):
		self.getPosition()
		return "Latest image file: " + self.getFullFileName()

	def isBusy(self):
		return self.detector.getStatus() == Detector.BUSY

       #Extra Impl

	def setFileFormat(self, fileExt, contents=2):
		'''
		fileExtension: 	dat: Raw data uncompressed
			 			png: PNG compressed
			 			tiff: TIFF compressed
			 			bmp: BMP uncompressed
			 			jpg: JPG compressed
			 			tif: TIFF uncompressed
		imagecontents: 	0: RGB 8+8+8 bits x,y,z, as seen on screen
			 			1: RGB 8+8+8 bits,x,y raw, z as seen on screen
			 			2: RAW 16 bits graylevel x, y, z raw data
		'''
		self.detector.setFileFormat(fileExt, contents);

	def setImageAverage(self, averageParameter):
		'''
		 averageParameter:	-1: Sliding average. Current does NOT work!
		 					0: No average
		 					1 ~ 99: Number of frames to be averaged
		'''
		self.detector.setImageAverageNumber(averageParameter);

	def getImageAverage(self):
		iv=self.detector.getImageAverageNumber();
		return iv;

	def protectCamera(self):
		#self.detector.setCollectionTime(0.1);
		self.detector.setCameraInProgress(True);
		if self.verbose:
			print "Camera is set to 'Recorder Mode' for protection.";
		return;


	def setAlive(self, newAlive=True):
		self.alive = newAlive;

	def setLogScale(self, newLogScale=True):
		self.logScale = newLogScale;

	def setPanel(self, newPanelName):
		self.panel = newPanelName;

	def getDetectorInfo(self):
		return self.detectorInfo;

	def singleFastShot(self, newExpos=None):
		if newExpos is not None: # New exposure time given
			self.exposureTime = newExpos;
			self.setCollectionTime(newExpos);
		return self.detector.shotSingleImage();


	def singleShot(self, newExpos=None):
		"""Shot single image with given exposure time""";

		#To put camera in the "camera mode"
		self.detector.setCameraInProgress(False);

		if self.getStatus() != Detector.IDLE:
			print 'Camera not available, please try later';
			return;

		if newExpos is not None: # New exposure time given
			self.exposureTime = newExpos;

		self.setCollectionTime(self.exposureTime);

		self.detector.setCameraSequentialMode(True);
		#self.setNumOfImages(1);
		self.collectData();

		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		if self.protection:
			self.protectCamera();

		return self.readout();

	def multiShot(self, numberOfImages, newExpos=None, newDir=True):
		"""Shot multiple images with given exposure time""";

		#To put camera in the "camera mode"
		self.detector.setCameraInProgress(False);

		if self.getStatus() != Detector.IDLE:
			print 'Camera not available, please try later';
			return;

		if newExpos is not None: # New exposure time given
			self.exposureTime = newExpos;

		self.setCollectionTime(self.exposureTime);

		if newDir:
			self.newImageDirectory();
			self.scanImageDirectory();
		else:
			self.detector.setCameraSequentialMode(True);


		temp=self.alive;
		self.alive=False;#To turn off the display

		if self.fastMode:
			fn=self.multiFastShot(numberOfImages);
		else:
			fn=self.multiSafeShot(numberOfImages);

		self.alive=temp; #To restoru the display setting

		if self.protection:
			self.protectCamera();

		return fn;

	def multiSafeShot(self, numberOfImages):
		fn=[];
		#self.setNumOfImages(numberOfImages);
		for n in range(numberOfImages):
			self.collectData();
			sleep(self.exposureTime);
			while self.getStatus() != Detector.IDLE:
				sleep(self.exposureTime/10.0);
			fn.append( self.readout() );

		return fn;

	def multiFastShot(self, numberOfImages):
		fn=[];
		#To take the first image
		self.collectData()
		sleep(self.exposureTime + 0.15);
		i=0;
		while i<numberOfImages-1:
			self.collectData();#To trigger a new acquisition
			t0=time.time();
			fn.append( self.readout() );#To save the previous picture
			t1=time.time();
			td=t1-t0;
			if td < self.exposureTime+0.15:#To wait the exposure time, plus a 150ms delay?
				sleep(self.exposureTime+0.15-td);
			i+=1;

		fn.append( self.readout() );#To save the last previous triggered picture
		return fn;

	def display(self,file=None):
		if file==None:
			file = self.getFullFileName()

		fileLoader = UViewDetectorClass.ImageFileLoaders[os.path.splitext(file)[-1].split('.')[-1].upper()];

		self.data.load( fileLoader(file) );

		dataset = self.data.getAxis(0);

		if self.panel:
			if self.logScale:
				RCPPlotter.imagePlot(self.panel, DatasetUtils.lognorm(dataset)); #For RCP GUI
			else:
				RCPPlotter.imagePlot(self.panel, dataset); #For RCP GUI
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));


	def setNumOfImages(self, number):
#		self.detector.setNumOfImages(number);
		return;

	def getNumOfImages(self):
		return 1
#		return self.detector.getNumOfImages();

#	To use the directory with scan number to save image, like what scan command does.
	def scanImageDirectory(self):
		#increase the scan number for one
		self.scanNumberTracker.incrementNumber();
		self.prepareForCollection();

#	To create a new directory following the PEEM image directory rules
	def newImageDirectory(self, newDir=None):
		if newDir is not None:
			self.detector.setImageDir(newDir);
		self.detector.prepare();

	def getFullFileName(self):
		"""Returns file path of the LAST CREATED image"""
		return self.fileName;
#		return self.detector.getFullFileName();



