from gda.device.scannable import ScannableUtils
from time import sleep
from gda.data import NumTracker
from gda.data import PathConstructor
from gda.jython import ScriptBase
from gda.factory import Finder
#setup the trajectory scan

class StorageServerStressTest(ScriptBase):
    def __init__(self, xmotor,trajController, daserver, xmap, xmapController):
        self.xmotor = xmotor
        self.trajController = trajController
        self.das = daserver
        self.xmap  = xmap
        self.xmapController = xmapController
        
    def doTrajectoryScan(self, start, stop, step, rowtime):
        nxsteps = ScannableUtils.getNumberSteps(self.xmotor,start, stop,step) + 1
        self.trajController.setM3Move(1)
        self.trajectory.setTotalElementNumber(nxsteps)
        self.trajectory.setTotalPulseNumber(nxsteps)
        self.checkForInterrupt()
        path = self.trajectory.defineCVPath(start, stop, rowtime)
        self.trajController.setMTraj(3,path)
        self.xmotorspeed.setSpeed(1.0)
        self.xmotor.asynchronousMoveTo(path[0])
        self.checkForInterrupt()
        self.trajController.setNumberOfElements((int)(self.trajectory.getElementNumbers()))
        self.trajController.setNumberOfPulses((int) (self.trajectory.getPulseNumbers()))
        self.trajController.setStartPulseElement((int) (self.trajectory.getStartPulseElement()))
        self.trajController.setStopPulseElement((int) (self.trajectory.getStopPulseElement()))
        self.checkForInterrupt()
        if (self.trajController.getStopPulseElement() != (int) (self.trajectory.getStopPulseElement())): 
            self.trajController.setStopPulseElement((int) (self.trajectory.getStopPulseElement()))          
        self.trajController.setTime((self.trajectory.getTotalTime()))
           
        self.checkForInterrupt()    
        self.trajController.build()
        while(self.trajController.getBuild() != 0):
            sleep(0.1)
            ##check the build status from epics
            self.checkForInterrupt()
        if(self.trajController.getBuildStatusFromEpics() != 1):
            print "Unable to buld the trajectory"
            self.checkForInterrupt()
            return
        self.setupDetectors(nxsteps, (rowtime) / nxsteps)
        self.tracController.execute()
        self.checkForInterrupt()
        while (self.tracController.getExecute() != 0):
            sleep(0.1)
            self.checkForInterrupt()
        self.tracController.read()
        self.checkForInterrupt()
        self.stopDetectors()
        #while (self.tracController.getRead() != 0):
#setup tfg
#setup xmap detector
    def setupXmapDetector(self, noOfPoints):
        #setup filename
        dataDir = PathConstructor.createFromDefaultProperty();
        dataDir = dataDir + "tmp/" ;
        dataDir = dataDir.replace("/dls/i18", "X:/");
        self.xmapController.setDirectory(dataDir);

        #Now lets try and setup the NumTracker...
        runNumber = NumTracker("tmp");
        #Get the current number
        scanNumber = runNumber.getCurrentFileNumber();
        lastRowNumber = scanNumber.getCurrentFileNumber()
        self.xmapController.setFilenamePostfix(lastRowNumber +"-"+self.xmap.getName());
        self.xmapController.setFileNumber(scanNumber);
        #setup counters
        self.xmapController.resetCounters()
        self.xmapController.setPixelsPerRun(noOfPoints)
        self.xmapController.setAutoPixelsPerBuffer(True)
        if(self.xmapController.isBufferedArrayPort()):
            self.xmapController.setHdfNumCapture(noOfPoints)
        else:
            buffPerRow = (noOfPoints ) / 124 + 1
            self.xmapController.setHdfNumCapture(buffPerRow)
        self.xmapController.startRecording()
        self.xmap.clearAndStart()
        
    def stopDetectors(self):
        self.das.sendCommand("tfg init")
        self.xmap.stop()
        self.xmapController.endRecording()
       
        
    def setupDaServer(self, noOfPoints):
        #setup daserver
        self.das.sendCommand("disable 0")
        self.das.sendCommand("clear 0")
        self.das.sendCommand("enable 0")
        self.das.sendCommand("tfg setup-trig start ttl0")
        self.das.sendCommand("tfg setup-groups ext-start cycles 1");
        self.das.sendCommand(noOfPoints + " 0.000001 0.00000001 0 0 0 8");
        self.das.sendCommand("-1 0 0 0 0 0 0");
        self.das.sendCommand("tfg arm");
        
    def checkForInterrupt(self):
        if(self.isInterrupted()):
            self.xmotor.stop()
            self.stopDetectors()
            #not sure if traj controller needs to be stopped
            #self.trajController.stop()
            self.checkForPauses()
            
#start the file writing
def ServerTestScan(yScannable, ystart, ystop, ystep, xScannable, xstart,xstop, xstep, rowTime):
    finder = Finder.getInstance()
    sssTest = StorageServerStressTest(xScannable,finder.find("epicsTrajectoryScanController"),
                                      finder.find("daserver"),finder.find("xmapMca"), finder.find("edxdcontroller"))
    noOfRows =  ScannableUtils.getNumberSteps(yScannable, ystart,ystop, ystep) + 1
    #yScannable.moveTo(ystart)
    #previousYPoint = ystart
    for rowNo in range(noOfRows):
        sssTest.checkForInterrupt()
        if(isOdd(rowNo)):
            sssTest.doTrajectoryScan( xstop,xstart,xstep, rowTime)
        else:
            sssTest.doTrajectoryScan(xstart, xstop, xstep, rowTime)
        
        #nextYPoint = ScannableUtils.calculateNextPoint(previousYPoint, ystep)
        #yScannable.moveTo(nextYPoint)
        #previousYPoint = nextYPoint
        
def isOdd(number):
    if(number % 2) == 0:
        return False
    return True
        