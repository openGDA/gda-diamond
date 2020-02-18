from time import sleep
from gdascripts.utils import caget, caput, caput_wait
from gda.device.scannable import ScannableBase

def setRequiredXmapPVs():
	try:
			caput_wait("ME13C-EA-DET-01:CollectMode", 0) #MCA Spectra
			caput_wait("ME13C-EA-DET-01:PresetMode", 1) #Real mode
			caput_wait("ME13C-EA-DET-01:MCA1.NUSE", 2048) #binning
			caput_wait("ME13C-EA-DET-01:DXP1:MaxEnergy", 20.48)
			caput_wait("ME13C-EA-DET-01:DXP2:MaxEnergy", 20.48)
			caput_wait("ME13C-EA-DET-01:DXP3:MaxEnergy", 20.48)
			caput_wait("ME13C-EA-DET-01:DXP4:MaxEnergy", 20.48)
	except:
		print "WARNING: Could not ensure xmapMca settings are correct"


enable_nexus()

setRequiredXmapPVs()
sleep(2)


class XmapPvSetter(ScannableBase):

	def __init__(self, name):
		self.name = name
		self.setOutputFormat({})
		self.setInputNames({})

	def atScanStart(self):
		setRequiredXmapPVs()

	def getPosition(self):
		return None

	def asynchronousMoveTo(self):
		return

	def isBusy(self):
		return False

xmapPvSetter = XmapPvSetter("xmapPvSetter")
add_default(xmapPvSetter)

############
# Live plot of spectrum so that it can be visualised during a scan without having to use
# The Epics screen

# Monitor a PVs containing array, plot the values using SDAPlotter when they change.
# Parameters to SDAPlotter are more or less the same as dnp.plot
# imh 27/11/2019

from gda.epics import CAClient
from org.eclipse.january.dataset import DatasetFactory
from uk.ac.diamond.scisoft.analysis import SDAPlotter
import random
from gov.aps.jca.event import MonitorListener

# MonitorListener to call updatePlot on callback from PV
class MonListener(MonitorListener) :
	def __init__(self, pvName, viewName='Live Plot'):
		self.caClient = CAClient(pvName)
		print("Live plot update set for: {} for plot name: {}".format(pvName, viewName))
		sleep(1)
		self.caClient.configure()
		sleep(1)
		self.monitor = self.caClient.camonitor(self)
		self.extraCaClients = []
		self.multiLinesPlot = True
		self.setViewName(viewName)


	def monitorChanged(self, event):
		if len(self.extraCaClients) > 0 :
			data = []
			data.append( getArray(self.caClient, self.shape[0]) )
			for client in self.extraCaClients :
				data.append( getArray(client, self.shape[0]) )
			if self.multiLinesPlot:
				plotLines(self.viewName, data)
				return
			else:
				plotXandYFromEpics(self.viewName, data[1], data[0])
				return

		if len(self.shape) == 1 :
			data = getArray(self.caClient, self.shape[0])
		else :
			data = get2DArray(self.caClient, self.shape[0], self.shape[1])

		# data = getRandomArray(self.numElements)
		plotData(self.viewName, data)

	def setShape(self, shape) :
		# List of dimensions
		self.shape = shape

	def getCaClient(self) :
		return self.caClient

	def setViewName(self, viewName) :
		self.viewName = viewName

	def removeMonitor(self) :
		print "Removing monitor for '%s'"%(self.viewName)
		self.caClient.removeMonitor(self.monitor)

	def addPv(self, pvName) :
		caclient = CAClient(pvName)
		caclient.configure()
		self.extraCaClients.append(caclient)


#remove monitor from last time the script was run
try :
	monListener.removeMonitor()
except :
	pass


# setup listener for 1d array data
basePv = "ME13C-EA-DET-01"
monListener = MonListener(basePv+":MCA1.VAL", "Xmap Live Plot")
monListener.setShape([16384])
monListener.addPv(basePv+":MCA1:XAXIS.VAL")
monListener.multiLinesPlot = False
#monListener.addPv(basePv+":ARR3:ArrayData")
#monListener.addPv(basePv+":ARR4:ArrayData")

# Generate Dataset of random values
def getRandomArray(numElements) :
	arr=[]
	for i in range(numElements) :
		arr.append(random.randrange(0, 100))
	dataset = DatasetFactory.createFromObject(arr, numElements)
	dataset.setName("random data")
	return dataset

# Return dataset filled with array of values from PV
def getArray(caclient, numElements) :
	# print "Getting data from "+caclient.getPvName()
	arr = caclient.cagetArrayDouble(numElements)
	dataset = DatasetFactory.createFromObject(arr, numElements)
	dataset.setName(caclient.getPvName())
	return dataset

def get2DArray(caclient, xsize, ysize) :
	# print "Getting data from "+caclient.getPvName()
	arr = caclient.cagetArrayDouble(xsize*ysize)
	dataset = DatasetFactory.createFromObject(arr, xsize, ysize)
	dataset.setName(caclient.getPvName())
	return dataset

# Send dataset to a plot
def plotData(view_name, dataset) :
	shape = dataset.getShape()
	if len(shape) == 1 :
		numElements = dataset.getShape()[0]
		# xDataset = DatasetFactory.createRange(0.0, numElements, 1.0)
		xDataset = DatasetFactory.createRange(0.0, numElements, 1.0)
		SDAPlotter.updatePlot(view_name, "array from "+dataset.getName(), [xDataset], [dataset], "x", "y")
	elif len(shape) == 2 :
		yAxisValues = DatasetFactory.createFromObject(range(0,shape[0]))
		xAxisValues = DatasetFactory.createFromObject(range(0,shape[1]))
		SDAPlotter.imagePlot(view_name, xAxisValues, yAxisValues, dataset)

# Send several datasets to a plot
def plotLines(view_name, datasets) :
	shape = datasets[0].getShape()
	numElements = shape[0]
	xDataset = DatasetFactory.createRange(0.0, numElements, 1.0)
	SDAPlotter.updatePlot(view_name, "", [xDataset], datasets, "x", "y")

def plotXandYFromEpics(view_name, xDataset, yDataset):
	SDAPlotter.updatePlot(view_name, "Array from "+yDataset.getName(), [xDataset], [yDataset], "Energy (keV)", "counts")

