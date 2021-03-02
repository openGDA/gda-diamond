from time import sleep, time;
import os;
from java.io import File;

from gda.data import NumTracker
from gda.jython import InterfaceProvider

from gda.device.detector import DetectorBase
from gda.device.detector.areadetector.v17 import NDPluginBase;
from gda.device import Detector

import scisoftpy as dnp;

from Diamond.Utility.Threads import BackgroundRunningTask
import sys

class ADDetectorDeviceClass(DetectorBase):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
	def __init__(self, name, ad_detector, panel_name="Fleacam"):

		self.setName(name);
		self.detector=ad_detector

		self.level = self.detector.getLevel() + 1;

		self.panel = panel_name;
		
		self.filePrefix = None;
		self.pathPostfix = None;
		self.fileName=None;
		self.filePath = name+"Image";
		self.fileFormat='%s%s%.5d.tif';
		self.delay = 0;

		self.dataHolder = None;
		self.dataset = None;

		self.width = 1024;
		self.height = 768;
		
		self.exposureTime = 1;

		self.alive = False;
		self.save = True;
		self.logScale = False;
		self.shifting = False;
		self.previewThread = None;
		
		self.stats = False;

		self.previouseImageMode=0;
		self.previouseAcquireStatus=0;

		self.extras=[];
		self.setup();

	def setup(self):
#		self.ndFile=self.detector.getNdFile();
#		self.ndArray=self.detector.getNdArray();
#		self.ndStats=self.detector.getNdStats();
		
		self.setInputNames([]);
		extra_names = ['ExposureTime', 'file'];
		extra_names.extend( self.extras );
		output_format = ['%f', '%s'];
		output_format.extend( ['%10.4f']*len(self.extras) );

		self.setExtraNames(extra_names);
		self.setOutputFormat(output_format);

	def setAlive(self, alive=True):
		self.alive = alive

	def setStats(self, stats=True):
		self.stats = stats;
		
		if self.stats == True:
			self.detector.setComputeCentroid(True);
			self.detector.setComputeStats(True);
			self.extras=['cen_x','cen_y','cen_sx','cen_sy', 'cen_sxy', 'mean','sigma', 'max','min','sum'];
			self.centroid=[None]*5;
			self.statistics=[None]*5;
		else:
			self.extras=[];

		self.setup();
		
	def setAcquirePeriod(self, newap):
		self.detector.getAdBase().setAcquirePeriod(newap)

	def getAcquirePeriod(self):
		return self.detector.getAdBase().getAcquirePeriod_RBV();

# Detector Implementation
	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, new_expos):
		self.exposureTime = new_expos;
		self.detector.setCollectionTime(self.exposureTime);
		ad_base=self.detector.getAdBase();

		if (ad_base.getAcquirePeriod_RBV() < self.exposureTime + 0.1 ):
			ad_base.setAcquirePeriod(self.exposureTime + 0.1)
		ad_base.setAcquireTime(self.exposureTime);


	def prepareForCollection(self):
		self.backupImageMode();
		self.setNewImagePath()
		self.detector.prepareForCollection();
		self.detector.getAdBase().setImageMode(0);
		self.prepareForSingleShot();
		
	def collectData(self):
		self.detector.collectData();

#	def asynchronousMoveTo(self,newExpos):
#		print "Please use .singleShot(newExposureTime)";
			
	def getStatus(self):
		return self.detector.getStatus();
	
	def readout(self):
#		print("Debug: "+  sys._getframe().f_code.co_name +" is called")

#		self.fileName=self.getFullFileName();
#		print "First attemp: " + self.fileName;
		if self.stats:
			self.getStatistics();
			self.getCentroid();

		sleep(self.delay);

		self.fileName=self.getFullFileName();
#		print("Second attemp: " + self.fileName)
			
		if self.alive:
			self.loadImageFile(self.fileName)
			self.display();
		
		result=[self.exposureTime, self.fileName];

		if self.stats:
			result.extend( self.centroid );
			result.extend( self.statistics );

		return result;

	def endCollection(self):
		print("Debug: "+  sys._getframe().f_code.co_name +" is called")
		self.enableNdFilePlugin(False, False);
		self.restoreImageMode();

	def stop(self):
		self.stopIt()
		self.endCollection();

	def atCommandFailure(self):
		self.stop();

#General camera operations:
	def display(self,dataset=None):
		if dataset is None:
			dataset=self.dataset;
			
		if dataset is None:
			print("No dataset to display")
			return;

		if self.panel:
			from uk.ac.diamond.scisoft.analysis import SDAPlotter 
			SDAPlotter.imagePlot(self.panel, dataset);
		else:
			print("No panel set to display")
			raise ValueError("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name, self.name));

	def stopIt(self):
		self.previewThread.stop();
		self.previewThread=None;

	def preview(self, expo, acq):
		if self.previewThread is not None:
			self.stopIt();
			
		self.previewThread=BackgroundRunningTask(self.previewLoop, [expo, acq]);
		self.previewThread.start();

	def previewLoop(self, t):
		new_expos, acquire_period=t;
		self.setCollectionTime(new_expos);
		self.prepareForPreview();
		
#		self.prepareForCollection();
#		self.collectData();
		
		while True:
			t0=time();
			self.getCameraData(); #To get the dataset
			self.display();
			lt= acquire_period - (time()-t0)/1000.;
			if lt >=0:
				sleep(lt);

	def prepareForPreview(self):
		#turn on the continuous viewing mode
		self.detector.prepareForCollection();
		self.detector.getAdBase().setImageMode(2);
		#turn off the NdFile plugin
		self.enableNdFilePlugin(False, False);
		#turn on the NdArray plugin
		self.enableNdArrayPlugin()

		self.detector.getAdBase().startAcquiring();

	def prepareForSingleShot(self):
		nd_file=self.detector.getNdFile();
		nd_file.setNumCapture(1);
		nd_file.setFileWriteMode(0); #Capture Mode: Single

		self.enableNdFilePlugin();

	def prepareForMultiShot(self, number_of_images):
		nd_file=self.detector.getNdFile();
		self.enableNdFilePlugin();
		nd_file.setNumCapture(number_of_images);
		nd_file.setFileWriteMode(1);#Capture Mode: Capture
		nd_file.startCapture()

	def singleShot(self, new_expos):
		self.setCollectionTime(new_expos);
		self.prepareForCollection();
		self.prepareForSingleShot()
		self.collectData();
		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		result=self.readout();
		self.endCollection();
		
		return result;

	def multiShot(self, new_expos, number_of_shots):
		self.setCollectionTime(new_expos);
		self.prepareForCollection();
		self.prepareForMultiShot(number_of_shots)
		self.collectData();
		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		result=self.readout();
		self.endCollection();
		
		return result;


#AdBase operation
	def getDimensions(self):
		ad_base=self.detector.getAdBase();
#		x=ad_base.getMaxSizeX_RBV();
#		y=ad_base.getMaxSizeY_RBV();
		x=ad_base.getArraySizeX_RBV();
		y=ad_base.getArraySizeY_RBV();
		z=ad_base.getArraySizeZ_RBV();
		
		if x == 0:
			x=ad_base.getMaxSizeX_RBV();
		if y == 0:
			y=ad_base.getMaxSizeY_RBV();
			
		return x,y,z;
		
#NdArray operations:
	def getCameraData(self):
		self.width, self.height, z = self.getDimensions();  # @UnusedVariable

		nd_array=self.detector.getNdArray();
		self.dataType=nd_array.getPluginBase().getDataType_RBV();
		
		t0=time();
		if self.dataType==NDPluginBase.UInt8:
#			print("Debug: Fetching UInt8 data started")
			self.rawData=nd_array.getByteArrayData( self.width*self.height )
			if self.shifting: #Need to cast the byte array to unsigned byte array  
				temp_double_list = [ float(x&0xFF) for x in self.rawData[0:self.width*self.height] ];
			else:
				temp_double_list = self.rawData[0:self.width*self.height];
		elif NDPluginBase.UInt16:
#			print("Debug: Fetch UInt16 data started")
			self.rawData=nd_array.getShortArrayData( self.width*self.height )
			if self.shifting: #Need to cast the short array to unsigned short array  
				temp_double_list = [ float(x&0xFFFF) for x in self.rawData[0:self.width*self.height] ];
			else:
				temp_double_list = self.rawData[0:self.width*self.height];
		else:
			print("Unknown data type")

		print("Dubug: Fetching data finished within %d seconds" %(time()-t0))

		da = dnp.array(temp_double_list);
		self.dataset = da.reshape([self.height, self.width]);

		return self.dataset;


	def enableNdArrayPlugin(self, callback=True, blocking=True):
		nd_array=self.detector.getNdArray();
		
		if callback:
			nd_array.getPluginBase().enableCallbacks();
		else:
			nd_array.getPluginBase().disableCallbacks();
		
		nd_array.getPluginBase().setBlockingCallbacks(blocking);

#NdFile operations:		
	def setFile(self, new_path_postfix, new_file_prefix):
		self.pathPostfix = new_path_postfix;
		self.filePrefix = new_file_prefix
		self.setNewImagePath();

	def resetImageNumber(self):
		self.imageNumber=0;#To reset the image number
		nd_file=self.detector.getNdFile();
		nd_file.setFileNumber(0);

	def enableNdFilePlugin(self, callback=True, blocking=True):
		nd_file=self.detector.getNdFile();
		
		if callback:
			nd_file.getPluginBase().enableCallbacks();
		else:
			nd_file.getPluginBase().disableCallbacks();
		
		nd_file.getPluginBase().setBlockingCallbacks(blocking);
			
		
	def setNewImagePath(self):
		"""Set file path and name based on current scan run number"""
		next_num = NumTracker("tmp").getCurrentFileNumber();
		
		base_path=InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator;
		sub_dir="%d_%s"%(next_num, self.pathPostfix); 
		new_image_path = os.path.join(base_path, sub_dir);

		if not os.path.exists(new_image_path):
			#print("Path does not exist. Create new one.")
			os.makedirs(new_image_path);
			self.resetImageNumber();
			
		if not os.path.isdir(new_image_path):
			print("Invalid path")
			return;
				
		self.filePath = new_image_path;
		#print("Image file path set to " + self.filePath)
		
		nd_file=self.detector.getNdFile();
		nd_file.setFilePath(self.filePath);
		nd_file.setFileName(self.filePrefix);
		nd_file.setFileTemplate(self.fileFormat);
		
		nd_file.setAutoIncrement(True);
		nd_file.setAutoSave(True);
		nd_file.setFileFormat(0);#Magic file format depending on the file extension
		return self.filePath;

	def backupImageMode(self):
		self.previouseImageMode=self.detector.getAdBase().getImageMode_RBV();
		self.previouseAcquireStatus = self.detector.getAdBase().getAcquireState();
		self.detector.getAdBase().stopAcquiring()
	
	def restoreImageMode(self):
		self.detector.getAdBase().setImageMode(self.previouseImageMode);
		if self.previouseAcquireStatus:
			self.detector.getAdBase().startAcquiring();

	def getFilePath(self):
		return self.detector.getNdFile().getFilePath_RBV();

	def getFullFileName(self):
		self.fileName=self.detector.getNdFile().getFullFileName_RBV();
		return self.fileName;

	def loadImageFile(self, file_name):
		if file_name is None:
			file_name=self.fileName;
			
		self.dataHolder=dnp.io.load(file_name);
		self.dataset = self.dataHolder[0];

		return self.dataset;

#NdStats operations:
	def getCentroid(self):
		self.ndStats=self.detector.getNdStats();
		centroid_x=self.ndStats.getCentroidX_RBV()
		centroid_y=self.ndStats.getCentroidY_RBV()
		centroid_sigma_x=self.ndStats.getSigmaX_RBV()
		centroid_sigma_y=self.ndStats.getSigmaY_RBV()
		centroid_sigma_x_y=self.ndStats.getSigmaXY_RBV()
		self.centroid=[centroid_x, centroid_y, centroid_sigma_x, centroid_sigma_y, centroid_sigma_x_y];

		return self.centroid;

	def getStatistics(self):
		self.ndStats=self.detector.getNdStats();
		stat_max=self.ndStats.getMaxValue_RBV()
		stat_min=self.ndStats.getMinValue_RBV()
		stat_total=self.ndStats.getTotal_RBV()
		stat_mean=self.ndStats.getMeanValue_RBV()
		stat_sigma=self.ndStats.getSigma_RBV()
		self.statistics=[stat_mean, stat_sigma, stat_max, stat_min, stat_total];
		
		return self.statistics;

