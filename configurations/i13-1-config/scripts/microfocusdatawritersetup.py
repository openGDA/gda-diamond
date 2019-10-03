#@PydevCodeAnalysisIgnore
from uk.ac.gda.client.microfocus.scan.datawriter import MicroFocusWriterExtender
from gda.factory import Finder
from gda.jython.commands.ScannableCommands import scan, add_default
from java.io import File
from java.lang import System
from gda.configuration.properties import LocalProperties
from jarray import array
from gda.jython import InterfaceProvider
from gda.factory import Finder
from java.io import File
from gdascripts.messages import handle_messages
from gda.jython.commands import ScannableCommands
import gda.device.Detector

from gda.jython import InterfaceProvider
from gda.device.scannable import ScanDataListenerScannable
from gda.configuration.properties import LocalProperties
class MFDWSetupScannable(ScanDataListenerScannable):
    def __init__(self, initialSelectedElement):
        self.setName("MFDWSetupScannable")
        self.mfd=None
        self.firstPointSeen = False
        self.initialSelectedElement = initialSelectedElement
        
    def createMFD(self, dims, detectorBeanFileName, initialSelectedElement):
        print "createMFD - dims:" + `dims`
        print "createMFD - detectorBeanFileName:" + detectorBeanFileName
        print "createMFD - initialSelectedElement:" + initialSelectedElement
        if len(dims) != 2:
            return None
        mfd = MicroFocusWriterExtender(dims[0], dims[1], 1, 1)
        mfd.setPlotName("DetectorPlot")
        mfd.setDetectorBeanFileName(detectorBeanFileName)
        print "createMFD - find"
        detectorList = [Finder.getInstance().find("mll_xmap")]
        print "createMFD - setDet"
        mfd.setDetectors(array(detectorList, gda.device.Detector))     
        print "createMFD - getWin"
        mfd.getWindowsfromBean()
#        mfd.setRoiNames(array(elements, java.lang.String))
        print "createMFD - setSel"
        mfd.setSelectedElement(initialSelectedElement)
        mfd.setEnergyValue(1.0)
        mfd.setZValue(0.) 
#        mfd.setRoiNames(array(elements, java.lang.String))
        
        
        return mfd
    
    def handleScanEnd(self):
        if self.mfd != None:
            self.mfd.completeCollection()
        self.mfd = None    
        self.firstPointSeen=False
    def handleScanDataPoint(self,scanDataPoint):
        print "handleScanDataPoint"
        if self.firstPointSeen and self.mfd == None:
            print "handleScanDataPoint - do nothing"
            return #not a valid scan
        self.firstPointSeen = True
        if self.mfd == None:
            print "handleScanDataPoint - create mfd"
            dims = self.getScanDimensions(scanDataPoint )
            self.mfd = self.createMFD(dims, LocalProperties.getVarDir() + "/vortex_parameters.xml", self.initialSelectedElement)
            if self.mfd == None:
                raise IOError("Unable to create MFD")
            jns=InterfaceProvider.getJythonNamespace()
            jns.placeInJythonNamespace("microfocusScanWriter", self.mfd)
        self.mfd.addData(None, scanDataPoint)
