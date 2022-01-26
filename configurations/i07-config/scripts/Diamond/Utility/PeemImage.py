
from time import sleep
import os;
import stat;
import math


#from gda.analysis.datastructure import *

from gda.analysis.io import PNGLoader, PNGSaver, JPEGLoader, TIFFImageLoader

from gda.analysis import ScanFileHolder
from org.eclipse.january.dataset import Maths as DatasetMaths

GDA_FILELOADERS={
			'TIF':TIFFImageLoader,
			'TIFF':TIFFImageLoader,
			'JPG':JPEGLoader,
			'JPEG':JPEGLoader,
			'PNG':PNGLoader
			}



class PeemImageClass(object):
	def __init__(self):
		self.data = ScanFileHolder();

	def fileExists(self, fileName, numberOfTry):
		result = False;
	
		for i in range(numberOfTry):
			if (not os.path.exists(fileName)) or (not os.path.isfile(fileName)):
				print "File does not exist on try " + str(i+1);
				#check again:
				sleep(1);
				os.system("ls -la " + fileName);
			else:
				#To check the file size non zero
				fsize = os.stat(fileName)[stat.ST_SIZE];
				#print "File exists on try " + str(i+1) + " with size " + str(fsize);
				if fsize == 0L:
					sleep(1);
					continue;
				#The file seems exist with some content inside. Double check to make sure it's available
				try:
					tf = open(fileName,"rb");
					tf.close();
					result = True;
					break;
				except:
					print "There are something wrong on the file system !!!"
					raise Exception("There are something wrong on the file system !!!");
		return result;
			

	def loadPNGFile(self, fileName):
		#To check file exist:
		if not self.fileExists(fileName, 5):
			print "File '" + fileName + "' does not exist!"
			raise Exception("No File Found Error");
		
		dataset = None;
		sfh = ScanFileHolder();
		sfh.load(PNGLoader(fileName));
		dataset = sfh.getAxis(0);
		return dataset;
	
	def savePNGFile(self, fileName, dataset):
		if os.path.exists(fileName) and os.path.isfile(fileName):
			print "File " + fileName + " already exist. Choose another name.";
			return False;
		
		#PNG file writer from GDA Analysis package
		sfh = ScanFileHolder();
		sfh.setAxis("PeemImage", dataset);
		sfh.save(PNGSaver(fileName));
		return True;


	def convert(self, fileX, fileY, fileRho, fileTheta):
		datasetX = self.loadPNGFile(fileX);
		datasetY = self.loadPNGFile(fileY);
		
		[datasetRho, datasetTheta] = self.getPolarDataset(datasetX, datasetY);
		
		r1 = self.savePNGFile(fileRho, datasetRho);
		r2 = self.savePNGFile(fileTheta, datasetTheta);
		if r1 and r2:
			print "Done";
		else:
			print "Abort";

	
	def getPolarDataset(self, datasetX, datasetY):
		datasetRho = DatasetMaths.sqrt( DatasetMaths.power(datasetX, 2) + DatasetMaths.power(datasetY, 2) );
		datasetTheta=DatasetMaths.arctan2(datasetY, datasetX);

		datasetThetaInDegree = DatasetMaths.toDegrees(datasetTheta);
		
		return [datasetRho, datasetThetaInDegree];
	
	def getPolarCoordinate(self, x, y):
		rho = math.sqrt(x**2 + y**2);
		theta = math.atan2(y, x);
		return [rho, self.degrees(theta)];
		
	def getCartesianCoordinate(self, rho, dTheta):
		theta = self.radians(dTheta);
		x=rho*math.cos(theta);
		y=rho*math.sin(theta);
		return [x, y];

	def degrees(self, radians):
		'Converts angle x from radians to degrees.'
		return radians * 180.0 / math.pi	

	def radians(self, degrees):
		'Converts angle x from degrees to radians.'
		return degrees * math.pi / 180.0

#Usage:
#peemImage = PeemImageClass();
#fnx = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000001.png"
#fny = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000002.png"
#fnr = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000001r.png"
#fnt = "/scratch/Dev/gdaDev/gda-config/i07/users/data/operation/Peem/ui00000001t.png"
#peemImage.convert(fnx, fny, fnr, fnt);
