from gda.analysis.datastructure import *
global sfc
sfc = ScanFileContainer()

def plotpil(scanNum):
	print "Plotting " + "/dls/i16/data/Pilatus/test"+str(scanNum) + ".tif"
	sfc.loadPilatusData("/dls/i16/data/Pilatus/test"+str(scanNum) + ".tif")
	sfc.plot()

def getpix(x,y):
	return sfc.getPixel(x,y)
	