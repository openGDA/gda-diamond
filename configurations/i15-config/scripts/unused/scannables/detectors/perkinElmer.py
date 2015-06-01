from gda.device.detector import DetectorBase
from gda.epics import CAClient
from os import path
from math import ceil
from time import sleep

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
        self.darkExpose = False
        self.skipExpose = False
        self.skippedAtStart = 0
        
        self.verbose=False

    def get_values(self):
        return self.name, self.pe

    def __repr__(self):
        return "PerkinElmer(name=%r, %r)" % (self.get_values())

    ###    DetectorBase implementations:

    def calculateSummedFramesNeeded(self):
        return int(ceil(self.collectionTime / self.pe.exposureTime_get()))

    def checkDarkMatches(self, summed):
        if summed != self.pe.darkSummed_get():
            print "#"*80
            print '# ERROR: New summed value %d is not the same' % summed, \
                  'as the last dark summed value %d' % self.pe.summed_get()
            print '# Collection was aborted - A new dark is required. Use:'
            print "-"*80
            print "darkExpose(%s, %f, 1, '%s')" % \
                (self.name, self.collectionTime,
                 path.join(self.relativePath, self.filePattern))
            print "#"*80
            raise

    def prepareForCollection(self):
        DetectorBase.prepareForCollection(self)
        if self.verbose:
            print "PerkinElmer.prepareForCollection started..."
        
        warnings = []
        
        if self.pe.skippedAtStart_get() != 0:
            warnings.append("WARNING: 'Skipped at Start' value %i is not 0!" %
                            self.pe.skippedAtStart_get())
            warnings.append("  GDA does not use the QXRD method of skipping")
            warnings.append("  frames so that trigger timing can be maintained.")
            warnings.append("  While this value is non-zero your images will")
            warnings.append("  not be synchronised with the movement of axes!")
        
        if self.pe.preTrigger_get() != 0:
            warnings.append("WARNING: Pre Trigger value %i is not 0!" %
                            self.pe.preTrigger_get())
        
        if self.pe.postTrigger_get() != 1:
            warnings.append("WARNING: Post Trigger value %i is not 1!" %
                            self.pe.preTrigger_get())
        
        if len(warnings) > 0:
            print "#"*80
            print "\n".join(warnings)
            print "#"*80
        
        # self.collectionTime doesn't appear to be set at this stage, so we
        # can't check this here.
        #if not self.darkExpose:
        #    self.checkDarkMatches(self.calculateSummedFramesNeeded())

    def collectData(self):
        """ Tells the detector to begin to collect a set of data, then returns
            immediately. """
        if self.verbose:
            print "PerkinElmer.collectData started...",
            print "skipExpose=%r," % self.skipExpose,
            print "darkExpose=%r" % self.darkExpose
        
        summed = self.calculateSummedFramesNeeded()
        
        if self.skipExpose:
            self.pe.summed_set(self.skippedAtStart)
        
        if self.darkExpose:
            self.pe.summed_set(summed)
            self.pe.darkSummed_set(summed)
        else:
            self.checkDarkMatches(summed)
        
        #outputDir = ntpath.join(self.outputDirRoot, self.relativePath)
        self.pe.outputDir_set(self.outputDir())
        if self.skipExpose:
            self.pe.filePattern_set(self.filePattern+"_skipped")
        else:
            self.pe.filePattern_set(self.filePattern)
        self.fileIndex = self.pe.fileIndex_get() # fileIndex is the next two be
        # written, so take a copy now.
        if self.darkExpose:
            self.pe.acquireDark()
            self.fileIndexExpectedToBeDifferent = False
        else:
            self.pe.acquire()
            self.fileIndexExpectedToBeDifferent = True

    def setCollectionTime(self, collectionTime):
        """ Sets the collection time, in seconds, to be used during the next
            call of collectData.
        self.collectionTime defined by DetectorBase """
        if self.verbose:
            print "PerkinElmer.setCollectionTime(%f) started..." % (collectionTime)
        
        DetectorBase.setCollectionTime(self, collectionTime)
        
        if not self.darkExpose:
            self.checkDarkMatches(self.calculateSummedFramesNeeded())

#    def getCollectionTime(self):
        """ Returns the time, in seconds, the detector collects for during the
            next call to collectData()
        self.collectionTime defined by DetectorBase """

    def getStatus(self):
        """ Returns the current collecting state of the device. BUSY if the
            detector has not finished the requested operation(s), IDLE if in
            an completely idle state and STANDBY if temporarily suspended. """
        if self.verbose:
            print "PerkinElmer.getStatus started... %r, %r, %i, %i, " % (
                self.fileIndexExpectedToBeDifferent, self.skipExpose,
                self.fileIndex, self.pe.fileIndex_get())
        if self.skipExpose:
            return self.BUSY
        if self.fileIndexExpectedToBeDifferent:
            if self.fileIndex == self.pe.fileIndex_get():
                return self.BUSY
        
        self.fileIndexExpectedToBeDifferent = False
        #if self.skipExpose:
        #    self.pe.fileIndex_set(self.fileIndex) # fileIndex is the next two be
        #    # written, so set it back to the previous values for skipped images.
        #    self.skipExpose = False # Also reset this value just to be sure.
        
        status = self.pe.status_get()
        if status == 1:
            return self.IDLE
        return self.BUSY

    def readout(self):
        """ Returns the latest data collected. The size of the Object returned
            must be consistent with the values returned by getDataDimensions
            and getExtraNames. """
        if self.verbose:
            print "PerkinElmer.readout started..."
        filePath = path.join(self.dataDir(), self.fileName(self.fileIndex))
        return filePath

    def getDataDimensions(self):
        """ Returns the dimensions of the data object returned by the readout()
            method. """
        if self.verbose:
            print "PerkinElmer.getDataDimensions started..."
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
        if self.verbose:
            print "createsOwnFiles started..."
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

    def outputDir(self):
        if self.skipExpose:
            return path.join(self.outputDirRoot, self.visitDir, "tmp")
        return path.join(self.outputDirRoot, self.visitDir, self.relativePath)

    def dataDir(self):
        return path.join(self.dataDirRoot, self.visitDir, self.relativePath)

    def fileName(self, fileIndex):
        suffix = ".dark.tif" if self.darkExpose else ".tif"
        return "%s-%05d%s" % (self.filePattern, fileIndex, suffix)

    def frameExposureTime(self, new_time_s=None):
        """Get or set the exposure time for individual Perkin Elmer frames.
        
        A single PE exposure is created by summing a number of frames equal
        to the exposure time divided by the frame exposure time.
        
        Example:
            >>> pe.frameExposureTime()
            0.1
            >>> pe.frameExposureTime(0.2)
            Changing frame exposure time from 0.1s to 0.2s
            0.2
         """
        if not new_time_s==None:
            print "Changing frame exposure time from %.4fs to %.4fs" % (
                self.pe.exposureTime_get(), new_time_s)
            self.pe.exposureTime_set(float(new_time_s))
            sleep(0.5)
        
        return self.pe.exposureTime_get()

    def framesSkippedAtStart(self, new_frames_skipped=None):
        """Enable or Disable the Perkin Elmer frame skipping functionality
        for expose(), simpleScan() and rockScan().
        
        Note this is not yet supported when using a standard GDA 'scan' command.
        
        If framesSkippedAtStart is non zero then before every image is taken, a
        dummy image of this many frames is taken with the fast shutter closed to
        ensure that any residual image on the PE sensor is eliminated or reduced.
        
        Example:
            >>> pe.framesSkippedAtStart()
            10
            >>> pe.framesSkippedAtStart(15)
            Changing the number of frames skipped at the start of each
            image from 10 to 15
            15
         """
        if not new_frames_skipped==None:
            if new_frames_skipped > 0:
                new_frames_skipped = int(new_frames_skipped)
            else:
                new_frames_skipped = 0
            print "Changing the number of frames skipped at the start of each"
            print "image from %i to %i" % (
                self.skippedAtStart, new_frames_skipped)
            self.skippedAtStart = new_frames_skipped
        
        return self.skippedAtStart

    def info(self):
        """
        Provide information on Perkin Elmer detector settings.
        """
        exposureTime = self.pe.exposureTime_get()
        summed = int(ceil(self.collectionTime / exposureTime))
        nextFileIndex = self.pe.fileIndex_get()
        print "PEPC Output Directory: %s" % self.outputDir()
        print "   DLS Data Directory: %s" % self.dataDir()
        print "        Next filename: %s" % self.fileName(nextFileIndex)
        print "  Frame Exposure Time: %.4fs" % exposureTime
        print " Last Collection Time: %.4fs (%iframes * %.4fs = %.4fs)" % (
            self.collectionTime, summed, exposureTime, exposureTime*summed)
        print "     Skipped at start: %i frames" % self.pe.skippedAtStart_get()
        print "                 Gain: %s" % self.pe.cameraGain_get()

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
        self.statusCA            = DummyCAClient(1)
        self.logFileCA           = DummyCAClient("")
        self.outputDirCA         = DummyCAClient("")
        self.filePatternCA       = DummyCAClient("")
        self.cameraGainRbvCA     = DummyCAClient("")
        self.exposureTimeCA      = DummyCAClient(1)
        self.exposureTimeRbvCA   = DummyCAClient(1)
        self.summedCA            = DummyCAClient(0)
        self.summedRbvCA         = DummyCAClient(0)
        self.preTriggerRbvCA     = DummyCAClient(0)
        self.postTriggerRbvCA    = DummyCAClient(1)
        self.fileIndexCA         = DummyCAClient(0)
        self.fileIndexRbvCA      = DummyCAClient(0)
        self.acquireCA           = DummyCAClient(0)
        self.skippedAtStartCA    = DummyCAClient(0)
        self.skippedAtStartRbvCA = DummyCAClient(0)
        self.darkSummedCA        = DummyCAClient(0)
        self.darkSummedRbvCA     = DummyCAClient(0)
        self.acquireDarkCA       = DummyCAClient(0)
        self.configure()

    def configure(self):
        self.statusCA.configure()
        self.logFileCA.configure()
        self.outputDirCA.configure()
        self.filePatternCA.configure()
        self.cameraGainRbvCA.configure()
        self.exposureTimeCA.configure()
        self.exposureTimeRbvCA.configure()
        self.summedCA.configure()
        self.summedRbvCA.configure()
        self.preTriggerRbvCA.configure()
        self.postTriggerRbvCA.configure()
        self.fileIndexCA.configure()
        self.fileIndexRbvCA.configure()
        self.acquireCA.configure()
        self.skippedAtStartCA.configure()
        self.skippedAtStartRbvCA.configure()
        self.darkSummedCA.configure()
        self.darkSummedRbvCA.configure()
        self.acquireDarkCA.configure()

    def __repr__(self):
        return "PerkinElmerInterfaceDummy()"

    def status_get(self):
        return int(self.statusCA.caget())

    def outputDir_set(self, value):
        logfile = path.join(value, "qxrd.log")
        self.outputDirCA.caput(value)
        self.logFileCA.caput(logfile)

    def filePattern_set(self, value):
        self.filePatternCA.caput(value)

    def cameraGain_get(self):
        return self.cameraGainRbvCA.caget()

    def exposureTime_set(self, value):
        self.exposureTimeCA.caput(value)

    def exposureTime_get(self):
        return float(self.exposureTimeRbvCA.caget())

    def summed_set(self, value):
        self.summedCA.caput(value)

    def summed_get(self):
        return int(self.summedRbvCA.caget())

    def preTrigger_get(self):
        return int(self.preTriggerRbvCA.caget())

    def postTrigger_get(self):
        return int(self.postTriggerRbvCA.caget())

    def fileIndex_set(self, value):
        self.fileIndexCA.caput(value)

    def fileIndex_get(self):
        return int(self.fileIndexRbvCA.caget())

    def fileIndex_reset(self):
        self.fileIndexCA.caput(0)

    def acquire(self):
        self.acquireCA.caput(1)

    def skippedAtStart_set(self, value):
        self.skippedAtStartCA.caput(value)

    def skippedAtStart_get(self):
        return int(self.skippedAtStartRbvCA.caget())

    def darkSummed_set(self, value):
        self.darkSummedCA.caput(value)

    def darkSummed_get(self):
        return int(self.darkSummedRbvCA.caget())

    def acquireDark(self):
        self.acquireDarkCA.caput(1)

class PerkinElmerInterface(PerkinElmerInterfaceDummy):

    def __init__(self):
        pv="BL15I-EA-PELM-01:"
        self.statusCA            = CAClient(pv+"STATUS")
        self.logFileCA           = CAClient(pv+"LOGFILE")
        self.outputDirCA         = CAClient(pv+"OUTPUTDIRECTORY")
        self.filePatternCA       = CAClient(pv+"FILEPATTERN")
        self.cameraGainRbvCA     = CAClient(pv+"CAMERAGAIN:RBV")
        self.exposureTimeCA      = CAClient(pv+"EXPOSURETIME")
        self.exposureTimeRbvCA   = CAClient(pv+"EXPOSURETIME:RBV")
        self.summedCA            = CAClient(pv+"SUMMEDEXPOSURES")
        self.summedRbvCA         = CAClient(pv+"SUMMEDEXPOSURES:RBV")
        self.preTriggerRbvCA     = CAClient(pv+"PRETRIGGERFILES:RBV")
        self.postTriggerRbvCA    = CAClient(pv+"POSTTRIGGERFILES:RBV")
        self.fileIndexCA         = CAClient(pv+"FILEINDEX")
        self.fileIndexRbvCA      = CAClient(pv+"FILEINDEX:RBV")
        self.acquireCA           = CAClient(pv+"ACQUIRE")
        self.skippedAtStartCA    = CAClient(pv+"SKIPPEDATSTART")
        self.skippedAtStartRbvCA = CAClient(pv+"SKIPPEDATSTART:RBV")
        self.darkSummedCA        = CAClient(pv+"DARKSUMMEDEXPOSURES")
        self.darkSummedRbvCA     = CAClient(pv+"DARKSUMMEDEXPOSURES:RBV")
        self.acquireDarkCA       = CAClient(pv+"ACQUIREDARK")
        self.configure()

    def __repr__(self):
        return "PerkinElmerInterface()"

def resetPEScanNumberFactory(pe):
    def resetPEScanNumber():
        pe.fileIndex_reset()
    
    return resetPEScanNumber