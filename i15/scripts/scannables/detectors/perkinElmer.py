from gda.device.detector import DetectorBase
from gda.epics import CAClient
from os import path
from math import ceil

class PerkinElmer(DetectorBase):
    
    def __init__(self, name, interface, outputDirRoot, dataDirRoot,
                 visitDir, relativePath, filePattern):
        self.name = name
        self.pe = PerkinElmerInterfaceDummy()
        self.pe = interface
        
        self.fileIndex = 0
        #self.outputDirRoot = "C:\ExperimentPE"
        self.outputDirRoot = outputDirRoot
        self.dataDirRoot = dataDirRoot
        self.visitDir = visitDir 
        self.relativePath = relativePath
        self.filePattern = filePattern
        
        self.fileIndexExpectedToBeDifferent = False
        #self.getStatusDiscardsRemaining = 0
        self.darkExpose = False

    def get_values(self):
        return self.name, self.pe

    def __repr__(self):
        return "PerkinElmer(name=%r, %r)" % (self.get_values())

    ###    DetectorBase implementations:

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        #print "collectData started..."
        summed = int(ceil(self.collectionTime / self.pe.exposureTime_get()))
        
        if self.darkExpose:
            self.pe.summed_set(summed)
            self.pe.darkSummed_set(summed)
        else:
            if summed != self.pe.summed_get():
                print "#"*80
                print '# ERROR: New summed value (%d)' % summed + \
                        ' is the not same as old (%d)' % self.pe.summed_get()
                print '# Collection was aborted - A new dark is required. Use:'
                print "-"*80
                print "darkExpose(%s, %f, 1, '%s')" % \
                    (self.name, self.collectionTime,
                     path.join(self.relativePath, self.filePattern))
                print "#"*80
                raise
        #outputDir = ntpath.join(self.outputDirRoot, self.relativePath)
        outputDir = path.join(self.outputDirRoot, self.visitDir, self.relativePath)
        self.pe.outputDir_set(outputDir)
        self.pe.filePattern_set(self.filePattern)
        self.fileIndex = self.pe.fileIndex_get() # fileIndex is the next two be
        # written, so take a copy now.
        if self.darkExpose:
            self.pe.acquireDark()
            self.fileIndexExpectedToBeDifferent = False
        else:
            self.pe.acquire()
            self.fileIndexExpectedToBeDifferent = True
        #self.getStatusDiscardsRemaining = 10

#    def setCollectionTime(self):
        """ Sets the collection time, in seconds, to be used during the next
            call of collectData.
        self.collectionTime defined by DetectorBase """

#    def getCollectionTime(self):
        """ Returns the time, in seconds, the detector collects for during the
            next call to collectData()
        self.collectionTime defined by DetectorBase """

    def getStatus(self):
        """ Returns the current collecting state of the device. BUSY if the
            detector has not finished the requested operation(s), IDLE if in
            an completely idle state and STANDBY if temporarily suspended. """
        #print "getStatus started..." + str(self.getStatusDiscardsRemaining)
        if self.fileIndexExpectedToBeDifferent:
            if self.fileIndex == self.pe.fileIndex_get():
                return self.BUSY
        self.fileIndexExpectedToBeDifferent = False
        #if self.getStatusDiscardsRemaining > 0:
        #    self.getStatusDiscardsRemaining -= 1
        #    return self.BUSY
        
        status = self.pe.status_get()
        if status == 1:
            return self.IDLE
        return self.BUSY

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        #print "readout started..."
        suffix = ".dark.tif" if self.darkExpose else ".tif"
        fileName = "%s-%05d%s" % (self.filePattern, self.fileIndex, suffix)
        filePath = path.join(self.dataDirRoot, self.visitDir, self.relativePath, fileName)
        return filePath

    def getDataDimensions(self):
        """ Returns the dimensions of the data object returned by the readout()
            method. """
        #print "getDataDimensions started..."
        return [ 1 ]

#    def prepareForCollection(self):
        """ Method called before a scan starts. May be used to setup detector
            for collection, for example MAR345 uses this to erase. """

#    def endCollection(self):
        """ Method called at the end of collection to tell detector when a
            scan has finished. Typically integrating detectors used in powder
            diffraction do not output until the end of the scan and need to be
            told when this happens. """

    def createsOwnFiles(self):
        """ Returns a value which indicates whether the detector creates its
            own files. If it does (return true) the readout() method returns
            the name of the latest file created as a string. If it does not
            (return false) the readout() method will return the data directly. """
        #print "createsOwnFiles started..."
        return True; 

    def getDescription(self):
        """ A description of the detector. """
        return "Perkin Elmer Epics/QXRD Detector";

    def getDetectorID(self):
        """ A identifier for this detector. """
        return "i15pe";

    def getDetectorType(self):
        """ The type of detector. """
        return "PerkinElmer";

class DummyCAClient:
    
    def __init__(self, returnValue):
        self.returnValue = returnValue
    
    def __repr__(self):
        return "DummyCAClient(returnValue=%r)" % (self.returnValue)

    def configure(self):
        pass
    
    def caget(self):
        return self.returnValue
    
    def caput(self, value):
        self.returnValue = value

class PerkinElmerInterfaceDummy:

    def __init__(self):
        self.statusCA       = DummyCAClient(1)
        self.outputDirCA    = DummyCAClient("")
        self.filePatternCA  = DummyCAClient("")
        self.exposureTimeCA = DummyCAClient(1)
        self.summedCA       = DummyCAClient(0)
        self.summedRbvCA    = DummyCAClient(0)
        self.fileIndexCA    = DummyCAClient(0)
        self.acquireCA      = DummyCAClient(0)
        self.darkSummedCA   = DummyCAClient(0)
        self.darkSummedRbvCA= DummyCAClient(0)
        self.acquireDarkCA  = DummyCAClient(0)
        self.configure()


    def configure(self):
        self.statusCA.configure()
        self.outputDirCA.configure()
        self.filePatternCA.configure()
        self.exposureTimeCA.configure()
        self.summedCA.configure()
        self.summedRbvCA.configure()
        self.fileIndexCA.configure()
        self.acquireCA.configure()
        self.darkSummedCA.configure()
        self.darkSummedRbvCA.configure()
        self.acquireDarkCA.configure()

    def __repr__(self):
        return "PerkinElmerInterfaceDummy()"

    def status_get(self):
        return int(self.statusCA.caget())

    def outputDir_set(self, value):
        self.outputDirCA.caput(value)

    def filePattern_set(self, value):
        self.filePatternCA.caput(value)

    def exposureTime_get(self):
        return float(self.exposureTimeCA.caget())

    def summed_set(self, value):
        self.summedCA.caput(value)

    def summed_get(self):
        return int(self.summedRbvCA.caget())

    def fileIndex_get(self):
        return int(self.fileIndexCA.caget())

    def fileIndex_reset(self):
        self.fileIndexCA.caput(0)

    def acquire(self):
        self.acquireCA.caput(1)

    def darkSummed_set(self, value):
        self.darkSummedCA.caput(value)

    def darkSummed_get(self):
        return int(self.darkSummedRbvCA.caget())

    def acquireDark(self):
        self.acquireDarkCA.caput(1)

class PerkinElmerInterface(PerkinElmerInterfaceDummy):

    def __init__(self):
        self.statusCA       = CAClient("BL15I-EA-PELM-01:STATUS")
        self.outputDirCA    = CAClient("BL15I-EA-PELM-01:OUTPUTDIRECTORY")
        self.filePatternCA  = CAClient("BL15I-EA-PELM-01:FILEPATTERN")
        self.exposureTimeCA = CAClient("BL15I-EA-PELM-01:EXPOSURETIME:RBV")
        self.summedCA       = CAClient("BL15I-EA-PELM-01:SUMMEDEXPOSURES")
        self.summedRbvCA    = CAClient("BL15I-EA-PELM-01:SUMMEDEXPOSURES:RBV")
        self.fileIndexCA    = CAClient("BL15I-EA-PELM-01:FILEINDEX:RBV")
        self.acquireCA      = CAClient("BL15I-EA-PELM-01:ACQUIRE")
        self.darkSummedCA   = CAClient("BL15I-EA-PELM-01:DARKSUMMEDEXPOSURES")
        self.darkSummedRbvCA= CAClient("BL15I-EA-PELM-01:DARKSUMMEDEXPOSURES:RBV")
        self.acquireDarkCA  = CAClient("BL15I-EA-PELM-01:ACQUIREDARK")
        self.configure()

    def __repr__(self):
        return "PerkinElmerInterface()"

def resetPEScanNumberFactory(pe):
    def resetPEScanNumber():
        pe.fileIndex_reset()
    
    return resetPEScanNumber