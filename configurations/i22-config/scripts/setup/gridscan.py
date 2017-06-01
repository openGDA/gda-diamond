import sys
import os.path
from gda.util.persistence import LocalParameters
import gda.configuration.properties.LocalProperties as lp

from gda.data.scan.datawriter import DataWriterExtenderBase
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.data.scan.datawriter import DataWriterFactory
from gda.factory import Finder
import gda.jython.commands.ScannableCommands.scan
from org.eclipse.dawnsci.analysis.dataset.roi import GridROI
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters
from gdascripts.messages import handle_messages
from gdascripts.scan import gdascans
from uk.ac.gda.server.ncd.subdetector import LastImageProvider
import scisoftpy as dnp
from org.eclipse.dawnsci.analysis.dataset.roi import GridPreferences
from uk.ac.diamond.scisoft.analysis import SDAPlotter as RCPPlotter
from java.util import HashMap
from org.eclipse.january.metadata import Metadata
class Grid(DataWriterExtenderBase):
	
	def __init__(self, cameraPanel, gridPanel, camera, positioner, ncddetectors):
		self.camera=camera
		self.positioner=positioner
		self.ncddetectors = ncddetectors
		self.iAmAGridThingy=True
		self.scanrunning=0
		self.cameraPanel = cameraPanel
		self.gridPanel = gridPanel
		dwfs=Finder.getInstance().getFindablesOfType(DataWriterFactory)
		for fac in dwfs.values():
			dwf=fac
			break
		extenders=dwf.getDataWriterExtenders()
		extenders=[ex for ex in extenders if not "iAmAGridThingy" in dir(ex)]
		extenders.append(self)
		dwf.setDataWriterExtenders(extenders)
		self.gridpreferencesStorage = LocalParameters.getXMLConfiguration('mappingGridPreferences')
		self.gridpreferencesStorage.autoSave = True
		try:
			self.loadPreferences()
		except Exception, e:
			#print e
			print "Using default grid preferences"
			self.gridpreferences = GridPreferences()
	
	def snap(self):
		try:
			image =  self.camera.readLastImage()
			if not self.gridpreferences == None:
				metadataMap = HashMap()
				metadataMap.put("GDA_GRID_METADATA", self.gridpreferences)
				image.setMetadata(Metadata(metadataMap))
				xs = image.getShape()[1]
				ys = image.getShape()[0]
				xbs = self.getBeamCentreX()
				ybs = self.getBeamCentreY()
				xres = self.getResolutionX()
				yres = self.getResolutionY()
				xa = dnp.array([(x-xbs)/xres for x in range(xs)])
				ya = dnp.array([(y-ybs)/yres for y in range(ys)])
				xa._jdataset().setName("mm")
				ya._jdataset().setName("mm")

				dnp.plot.image(image, x=xa, y=ya, name=self.cameraPanel)
			else:
				dnp.plot.image(image, name=self.cameraPanel)
		except Exception, e:
			print "  gridscan: error getting camera image"
			print e.message
		
		
	def scan(self, roi=None):
		if roi is None:
			beanbag=dnp.plot.getbean(name=self.cameraPanel)
			if beanbag == None:
				print "No Bean found on "+self.cameraPanel+" (that is strange)"
				return
			try:
				roi=beanbag[GuiParameters.ROIDATA]._jroi()
			except AttributeError:
				print "No ROI selected - has grid been deleted?"
				return

		if not isinstance(roi, GridROI):
			print "no Grid ROI selected"
			return
		if self.scanrunning:
			print "Already Running"
			return
		self.gridpreferences = roi.getGridPreferences()
		print "Beam centre: %d, %d  Resolution px/mm: %5.5f %5.5f" % (self.getBeamCentreX(), self.getBeamCentreY(), self.getResolutionX(), self.getResolutionY())
		self.scanrunning=True
		try:
			points=roi.getPhysicalGridPoints()
			self.dimensions=roi.getDimensions()
			self.dimensions=[self.dimensions[1],self.dimensions[0]]
			try:
				bc = roi.getBeamCentre()
				self.camera.setAttribute("beam_center_x", bc[0])
				self.camera.setAttribute("beam_center_y", bc[1])
				ps = roi.getPixelSizeM()
				self.camera.setAttribute("x_pixel_size", ps[0])
				self.camera.setAttribute("y_pixel_size", ps[1])
			except:
				pass
			print "Scanning a %d by %d grid" % tuple(self.dimensions)
			RCPPlotter.setupNewImageGrid(self.gridPanel,self.dimensions[0],self.dimensions[1])
			xpoints = sorted(set(x[0] for x in points))
			ypoints = sorted(set(y[1] for y in points))
			gdascans.Rscan()(self.positioner.x, tuple(xpoints), self.positioner.y, tuple(ypoints), self.ncddetectors, self.camera)
		except:
			type, exception, traceback = sys.exc_info()
			self.scanrunning = False
			handle_messages.log(None, "Error in grid_scan.scan", type, exception, traceback, False)		

	def scanAll(self):
		beanbag=dnp.plot.getbean(name=self.cameraPanel)
		if beanbag == None:
			print "No Bean found on "+self.cameraPanel+" (that is strange)"
			return
		#cur = beanbag[GuiParameters.ROIDATA]._jroi()
		roiDataList = beanbag[GuiParameters.ROIDATALIST]
		if not roiDataList:
			print "No ROIs found"
			return
		
		roiList = [g._jroi() for g in roiDataList]
		gRoiList = []
		for roi in roiList:
			if isinstance(roi, GridROI):
				gRoiList.append(roi)
		
		if gRoiList:
			print "Scanning %d grid(s)\n" % len(gRoiList)
			for roi in gRoiList:
				self.scan(roi)
				print
			print "Completed scanning"
		else:
			print "no Grid ROIs"
			
	def getSaxsDetector(self):
		for det in self.ncddetectors.getDetectors():
			if det.getDetectorType() == "SAXS":
				return det
		raise Exception("Unable to find SAXS detector in ncddetectors")
	
	def getSaxsDetectorName(self):
		return self.getSaxsDetector().getName()

	def addData(self, parent, dataPoint):
		if not self.scanrunning:
			return
		try:
				pno=dataPoint.getCurrentPointNumber()
				index=dataPoint.getDetectorNames().indexOf(self.ncddetectors.getName())
				tree=dataPoint.getDetectorData().get(index).getNexusTree()
				try:
					data=tree.findNode("detector").findNode("data").getData()
					ds = dnp.array(data.getBuffer().tolist())
					ds.shape = data.dimensions.tolist()[1],data.dimensions.tolist()[2]
				except:
					if isinstance(self.getSaxsDetector(), LastImageProvider):
						ds=self.getSaxsDetector().readLastImage()
				if ds is not None:
					RCPPlotter.plotImageToGrid(self.gridPanel,ds._jdataset(),pno/self.dimensions[0],pno%self.dimensions[0],True)
		except:
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None, "Error in grid_scan.addData", type, exception, traceback, False)		

	def completeCollection(self, parent):
		if self.scanrunning:
			self.scanrunning=False
			print "Grid scan complete"
			
	def getBeamCentreX(self):
		return self.gridpreferences.getBeamlinePosX()
	def getBeamCentreY(self):
		return self.gridpreferences.getBeamlinePosY()
	def setBeamCentreX(self, x):
		self.gridpreferences.setBeamlinePosX(x)
		self.updatePreferences()
	def setBeamCentreY(self, y):
		self.gridpreferences.setBeamlinePosY(y)
		self.updatePreferences()
		
	def getResolutionX(self):
		return self.gridpreferences.getResolutionX()
	def getResolutionY(self):
		return self.gridpreferences.getResolutionY()
	def setResolutionX(self, x):
		self.gridpreferences.setResolutionX(x)
		self.updatePreferences()
	def setResolutionY(self, y):
		self.gridpreferences.setResolutionY(y)
		self.updatePreferences()
	
	def updatePreferences(self):
		self.savePreferences()
		self.snap()
	
	def loadPreferences(self):
		gp = GridPreferences()
		gps = self.gridpreferencesStorage
		gp.setBeamlinePosX(gps.getDouble('beamlinePosX', 0))
		gp.setBeamlinePosY(gps.getDouble('beamlinePosY', 0))
		gp.setResolutionX(gps.getDouble('resolutionX', 1))
		gp.setResolutionY(gps.getDouble('resolutionY', 1))
		self.gridpreferences = gp

	def savePreferences(self):
		gp = self.gridpreferences
		gps = self.gridpreferencesStorage
		for prop in ['beamlinePosX', 'beamlinePosY', 'resolutionX', 'resolutionY']:
			if not gps.containsKey(prop) or gps.getDouble(prop) != getattr(gp, prop):
				gps.setProperty(prop, getattr(gp, prop))
