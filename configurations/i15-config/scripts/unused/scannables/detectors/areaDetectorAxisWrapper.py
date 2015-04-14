from __future__ import with_statement
import os, re, sys
from threading import Thread
from time import sleep
from gdascripts.messages.handle_messages import simpleLog, log
from gda.epics import CAClient
from operationalControl import moveMotor
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setVelocity
from gda.data.fileregistrar import FileRegistrarHelper
from scannables.detectors.detectorAxisWrapperNew import DetectorAxisWrapperNew
from marAuxiliary import openMarShield as openPeShield, closeMarShield as closePeShield

class AreaDetectorAxisWrapper(DetectorAxisWrapperNew):
    def __init__(self, detector, isccd, prop, feabsb, fmfabsb, exposureTime=1,
                 axis=None, step=None, sync=False, fileName="pe_scan",
                 noOfExpPerPos=1, rock=False, pause=False, exposeDark=False):
        
        DetectorAxisWrapperNew.__init__(self, detector, isccd, prop, feabsb,
            fmfabsb, pause, -11, exposureTime, step, axis, sync, exposeDark)
        self.fileName = fileName
        #self.fullFileName = ""
        self.exposureNo = 1
        self.noOfExpPerPos = noOfExpPerPos
        #self.nextScanNo = getNextMarScanNumber()
        self.inc = 1;
        self.setName("area detector wrapper")
        self.rock=rock
        
        self.caclient = CAClient()
        self.diodeSum = "BL15I-DI-PHDGN-01:DIODESUM"
        # Note, this PV currently reads the BL15I-DI-PHDGN-01:I PV. If you want
        # to sum another PV, use BL15I-EA-CSTRM-01:DIODECALC.INPB to set the PV
        # you want to sum atScanStart.

    def atScanStart(self):
        DetectorAxisWrapperNew.atScanStart(self)
        # Zero the diode sum we can tell if it was triggered
        self.caclient.caput(self.diodeSum, 0) 
        self.detector.prepareForCollection()
        if not self.exposeDark:
            openPeShield()
        else: # Just in case the shield is still open from a failed expose()
            closePeShield() 

    def atScanEnd(self):
        DetectorAxisWrapperNew.atScanEnd(self)
        closePeShield()

    def acquireOneImage(self, position):
        #if self.detector.verbose:
        simpleLog("AreaDetectorAxisWrapper.acquireOneImage(%r)" % position)
        runUp = ((self.velocity*.25)/2) + 0.1 # acceleration time .25 may
        #change. This seems to solve the problem of the fast shutter not
        #staying open.
        
        #self.detector.darkExpose = False
        
#        if self.detector.skippedAtStart > 0:
#            simpleLog("Acquiring dummy image to clear last acquisition...")
#            self.detector.skipExpose = True
#            self.detector.collectData()
#            #sleep(self.detector.skippedAtStart *
#            #      self.detector.pe.exposureTime_get())
#            simpleLog("Waiting for area detector status idle after dummy image")
#            #while self.detector.getStatus():
#            while self.detector.fileIndex == self.detector.pe.fileIndex_get():
#                sleep(0.5)
#                print ".",
#            print "."
#            
#            simpleLog("Resetting fileIndex")
#            self.detector.pe.fileIndex_set(self.detector.fileIndex) # fileIndex
#            # is the next two be written, so set it back to the previous values
#            # after acquiring a skipped image.
#            while self.detector.fileIndex != self.detector.pe.fileIndex_get():
#                sleep(0.5)
#                print ".",
#            print "."
#            self.detector.skipExpose = False
        
        #self.detector.darkExpose = self.exposeDark
        
        #if self.detector.verbose:
        simpleLog("Setting collection time...")
        
        self.detector.setCollectionTime(self.exposureTime)
        
        #if self.detector.verbose:
        simpleLog("Acquiring image...")
        
        if self.sync:
            setMaxVelocity(self.axis)
            deactivatePositionCompare() #Prevent false triggers when debounce on
            moveMotor(self.axis, position - runUp)
            scanGeometry(self.axis, self.velocity, position , position + self.step)
            sleep(0.2)
            self.isccd.xpsSync("dummy", self.exposureTime)
            
            self.preExposeCheck()
            
            self.detector.collectData()
            moveMotor(self.axis, position + self.step + runUp)
            
            deactivatePositionCompare()
            
        elif self.axis:
            simpleLog("(fast shutter not synchronised with motor)")
            setMaxVelocity(self.axis)
            moveMotor(self.axis, position - runUp)
            setVelocity(self.axis, self.velocity)
            self.isccd.openS()
            
            self.detector.collectData()
            moveMotor(self.axis, position + self.step + runUp)
            
            self.isccd.closeS()
            
        elif self.exposeDark:
            self.detector.collectData()
            sleep(self.exposureTime+0.1)
        else:
            self.isccd.openS()
            self.detector.collectData()
            sleep(self.exposureTime)
            self.isccd.closeS()
        
        #if self.detector.verbose:
        simpleLog("Waiting for area detector status idle")
        while self.detector.getStatus():
            sleep(0.5)
            print ".",
        print "."
        #if self.detector.verbose:
        simpleLog("Detector idle")
        
        # Since the scanning mechanism calls the detector readout, do we need
        # this here too?
        self.detector.readout()
        #if self.detector.verbose:
        simpleLog("Readout complete")

    def rawAsynchronousMoveTo(self, position):
        if type(position) == list:
            if self.sync:
                simpleLog("rawAsynchronousMoveTo(%r) returning..." % position)
                setMaxVelocity(self.axis)
                moveMotor(self.axis, position[1])
            else:
                simpleLog("rawAsynchronousMoveTo(%r) returning early." % position)
            return
        
        self.files = []
        
        for exp in range(self.noOfExpPerPos):
            
            if self.velocity <= 8.0:
            
                self.isccd.flush()
                
                simpleLog("Ignoring filename '%r'" % self.fileName)
                #split = os.path.split(self.fileName)
                #visitDir = self.visitPath.replace(self.detector.dataDirRoot+"/","")
                #self.detector.visitDir = visitDir
                #self.detector.relativePath = split[0]
                #self.detector.filePattern = split[1]
                
                self.acquireOneImage(position)
                
                if self.postExposeCheckFailed():
                    self.acquireOneImage(position)
                
                filename = self.detector.readout()
                self.files.append(filename)
                #if self.detector.verbose:
                simpleLog("self.files=%r @ exp=%d" % (self.files, exp))
                FileRegistrarHelper.registerFile(filename)
                
                # expose(pe, 5, 1, "tmp/pe_mbb_expose")
                # expose(pe, 5, 2, "tmp/pe_mbb_expose")
                # rockScan(dkphi, 58, 3, 1, pe, 5, "tmp/pe_mbb_rockScan")
                # simpleScan(dkphi, 58, 60, 1, pe, 5, 1, "tmp/pe_mbb_simpleScan")
                diodeSum=self.caclient.caget(self.diodeSum)
                self.ModifyMetadata(filename, diodeSum).start()
            else:
                simpleLog("velocity too high, please specify a longer exposure time (max velocity of kphi=8.0 deg/sec)")
            
            self.exposureNo += 1
        
        self.inc +=1

    class ModifyMetadata(Thread):
        def __init__(self, filename, value):
            Thread.__init__(self)
            self.value = value
            self.filename = filename
        
        def run(self):
            filename = "%s.metadata" % self.filename
            simpleLog("Modifying metadata userComment4=%s in %r" %
                      (self.value, filename))
            try:
                # Note that the metadata file is DOS CRLF not LF only
                regex = re.compile("^(userComment4=)(\r)$", re.MULTILINE)
                subst = "\g<1>%s\g<2>" % self.value
                
                with open(filename) as f:
                    text = f.read()
                
                if len(regex.findall(text)) == 1:
                    os.rename(filename, filename+".bak")
                    text = re.sub(regex, subst, text)
                    with open(filename, "w") as f:
                        f.write(text)
                    simpleLog("Completed " + filename)
                else:
                    simpleLog("userComment4 not found in " + filename)
            except:
                typ, exception, traceback = sys.exc_info()
                log(None, "Unable to modify metadata: ", typ, exception, traceback)
                simpleLog("!"*80)
                simpleLog("WARNING: metadata modify failed for: %r" % filename)
                simpleLog("         Note that userComment4=%s" % self.value)
                simpleLog("!"*80)

    def rawIsBusy(self):
        return self.detector.getStatus();
