from temporarySrsReader import createSrsPath, readSrsDataFile
from gda.analysis.io import JPEGLoader, TIFFImageLoader
from org.eclipse.dawnsci.analysis.api.io import ScanFileHolderException
from gda.analysis import ScanFileHolder
from org.eclipse.january.dataset import DatasetFactory
from gdascripts.scan.process.ScanDataProcessor import loadScanFile
from gda.analysis import ScanFileHolder
from gda.analysis.io import SRSLoader
from gda.analysis import RCPPlotter
from gda.configuration.properties import LocalProperties

def loadSrsColumn(path, columnName):
	columnNames, data = readSrsDataFile(path)
	return data[columnNames.index(columnName)]


def loadScan(scanID):
	path = createSrsPath(scanID)
	print "loading scan file: ", path
	sfh = ScanFileHolder()
	sfh.load(SRSLoader(path))
	return sfh, loadSrsColumn(path, 'path')

def loadImage(path):
	print "loading image: ", path
	sfh = ScanFileHolder()
	sfh.load(TIFFImageLoader(path))
	return sfh[0]

def loadScanAndImages(scanID, root_path = None):
	"""Load scan data drom scanID (can be a scan path or number (0 for last). Returns sfh, imagestack"""
	sfh, relativeImagePaths = loadScan(0)
	if root_path is None:
		absImagePaths = relativeImagePaths
	else: 
		absImagePaths = [root_path + relpath for relpath in relativeImagePaths]
	imagestack = loadImageStack(absImagePaths)
	return sfh, imagestack

def loadImageStack(pathList):
	height, width = loadImage(pathList[0]).getDimensions()
	imagestack = DatasetFactory.zeros(len(pathList), height, width)
	imagestack.setName('imagestack')
	imagestack.fill(-1)
	print "Creating image stack [images][height][width] = [%i][%i][%i]" % (len(pathList), height, width)
	for i in range(len(pathList)):
		image = loadImage(pathList[i])
		RCPPlotter.imagePlot('Pilatus Plot', image)
		image.shape = [1, height, width]
		imagestack[i:i+1,:,:] = image
	return imagestack 

newTechniqueHelp = """
>>> from new_technique import *
>>> sfh, relativeImagePaths = loadScan(0)
>>> absImagePaths = [ipp.root_datadir + relpath for relpath in relativeImagePaths]

"""