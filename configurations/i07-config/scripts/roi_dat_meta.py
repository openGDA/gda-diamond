from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.factory import Finder
from gda.device.detector.nexusprocessor.roistats import RegionOfInterest
import json

"""
This is a scannable intended to be added metadata for the purpose
of recording region of interest metadata in the datafile.
It is also written to the NXdetector directly for the Nexus file.
"""
class RoiMetaDatFileDevice(ScannableBase):

	def __init__(self, name, det_name, plot_name):
		self.name = name

		"""List of detector names to be checked if present in a scan"""
		self.plot_name = plot_name
		self.setInputNames({})
		self.setOutputFormat(["%s"])
		self.setExtraNames([det_name + "_ROIs"])

	def isBusy(self):
		return False

	def rawAsynchronousMoveTo(self, position):
		pass

	def getPosition(self):
		return json.dumps({r.getName(): {"x": r.getX(), "y": r.getY(), "width": r.getWidth(), "height": r.getHeight()} for r in RegionOfInterest.getRoisForPlot(self.plot_name)})

