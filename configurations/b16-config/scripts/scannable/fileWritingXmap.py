from __future__ import with_statement 
from gda.device.detector import DetectorBase
from gda.device.scannable import ScannableMotionBase
import os.path
from gda.data import NumTracker 
from gda.jython import InterfaceProvider
import time

# For example::
#
#    >>>import scannable.fileWritingXmap
#    >>>xmap = scannable.fileWritingXmap.FileWritingXmap("xmap", xmapMca)
#    >>>scannable.fileWritingXmap.configureScannableLevels(x ,y)
#    
#    >>>scan y 1. 4 1 x 5. 6 1 xmap.exp 1.23 ai1l ai2l ai3l xmap
#    Writing data to file:/scratch/ws/8_4/users/data/29.dat
#         x         y      exp      ai1l      ai2l      ai3l                                                               xmap
#    5.0000    1.0000    1.230    87.588    62.939    31.708    /scratch/ws/8_4/users/data/mca/29/row0/29_yindex_0_xindex_0.mca
#    6.0000    1.0000    1.230    77.363    54.137    51.988    /scratch/ws/8_4/users/data/mca/29/row0/29_yindex_0_xindex_1.mca
#    5.0000    2.0000    1.230    77.363    54.137    51.988    /scratch/ws/8_4/users/data/mca/29/row1/29_yindex_1_xindex_2.mca
#    6.0000    2.0000    1.230    77.363    54.137    51.988    /scratch/ws/8_4/users/data/mca/29/row1/29_yindex_1_xindex_3.mca
#    5.0000    3.0000    1.230    2.6279    3.1916    29.335    /scratch/ws/8_4/users/data/mca/29/row2/29_yindex_2_xindex_4.mca
#    6.0000    3.0000    1.230    2.6279    3.1916    29.335    /scratch/ws/8_4/users/data/mca/29/row2/29_yindex_2_xindex_5.mca
#    5.0000    4.0000    1.230    2.6279    3.1916    29.335    /scratch/ws/8_4/users/data/mca/29/row3/29_yindex_3_xindex_6.mca
#    6.0000    4.0000    1.230    2.6279    3.1916    29.335    /scratch/ws/8_4/users/data/mca/29/row3/29_yindex_3_xindex_7.mca
#    Scan complete.


def configureScannableLevels(x ,y):
    """Makes sure that, if y is used as an outer loop to x's inner, x appears first in the resulting srs file
    """
    x.setLevel(y.getLevel() - 1)


class CollectionTimeScannable(ScannableMotionBase):
    
    def __init__(self, name, fileWritingXmap):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ["%.3f"]
        self.fileWritingXmap = fileWritingXmap
    
    def asynchronousMoveTo(self, t):
        self.fileWritingXmap.setCollectionTime(t)
    
    def getPosition(self):
        return self.fileWritingXmap.getCollectionTime()
    
    def isBusy(self):
        return False


class FileWritingXmap(DetectorBase):
    
    def __init__(self, name, xmapDetector):
        self.name = name
        self.inputNames = [name]
        self.extraNames = []
        self.outputFormat = ["%s"]
        
        self.xmapDetector = xmapDetector
        self.exp = CollectionTimeScannable("exp", self)
        self.scanNumTracker = NumTracker("tmp")
        self.row = None
        self.point = None
        self.collectionTime = 0.0
        
    def __clearCounters(self):
        self.row = None
        self.point = None
###        
    def atScanStart(self):
        self.row = 0
        self.point = 0
        
    def atScanLineEnd(self):
        self.row += 1
        
    def atPointEnd(self):
        self.point += 1
        
    def atScanEnd(self):
        self.__clearCounters()
        
    def atCommandFailure(self):
        self.__clearCounters()
    
    def asynchronousMoveTo(self, t):
        self.setCollectionTime(t) # as DetectorBase does not
        self.collectData()
        #time.sleep(1.0)
###
    def setCollectionTime(self, t):
        self.collectionTime = t
        self.xmapDetector.setCollectionTime(t)
        
    def getCollectionTime(self):
        return self.xmapDetector.getCollectionTime()
    
    def collectData(self):
        self.xmapDetector.collectData()
    
    def getStatus(self):
        time.sleep(self.collectionTime + 0.3)
        return self.xmapDetector.getStatus()
    
    def writesOwnFiles(self):
        return True
    
    def readout(self):
        """Reads spectra out of the xmap detector and then writes them to a single file and returns this file's path.
        """
        #time.sleep(0.1)
        self.xmapDetector.stop()
        dir = self.__getDirectory()
        if not os.path.exists(dir):
            os.makedirs(dir)
        path = os.path.join(dir, self.__getFilename())
        self.__writeData(path)
        return path
###
    def __getDirectory(self):
        scannumber = int(self.scanNumTracker.getCurrentFileNumber())
        return os.path.join(InterfaceProvider.getPathConstructor().createFromDefaultProperty(), 'mca', `scannumber`, 'row' +`self.row`)
    
    def __getFilename(self):
        scannumber = int(self.scanNumTracker.getCurrentFileNumber())
        return `scannumber` + '_yindex_' + `self.row` + '_xindex_' + `self.point` + '.mca'
    
    def __writeData(self, absFilename):
        vortexSpectra = self.xmapDetector.getData()
        with open(absFilename, 'a') as f:
            for spectrum in vortexSpectra:
                print >> f, ' '.join(map(str, spectrum))    
