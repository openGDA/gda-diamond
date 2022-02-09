from time import sleep
from datetime import datetime
from gda.device.monitor import EpicsMonitor
from gda.device.enumpositioner import EpicsSimpleMbbinary
from gda.device.scannable import ScannableMotionBase
from iviumI16.EpicsDevices import EpicsDeviceClass


class IviumPotentiastat:
    """A potentiostat class for the Ivium CompactStat (one channel)"""
    def __init__(self, pvStem):
        self.pvStem = pvStem

        
    def setMethodMode(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":OperatingMode",1) #Method
            caput(self.pvStem+"PORT"+str(i)+":ImageMode",1) #Multiple
            caputS(self.pvStem+"HDF"+":FileTemplate","%s%s.hdf")
            sleep(0.1)
            caput(self.pvStem+"HDF"+":EnableCallbacks",1)
            caput(self.pvStem+"HDF"+":FileWriteMode",2)
            caput(self.pvStem+"HDF"+":LazyOpen",1)
            
    def setDirectMode(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":OperatingMode",0) #Direct
            caput(self.pvStem+"PORT"+str(i)+":ImageMode",2) #Continuous
            caputS(self.pvStem+"HDF"+":FileTemplate","%s%s.hdf")
            sleep(0.1)
            caput(self.pvStem+"HDF"+":EnableCallbacks",1)
            caput(self.pvStem+"HDF"+":FileWriteMode",2)
            caput(self.pvStem+"HDF"+":LazyOpen",1)
            caput(self.pvStem+"PORT"+str(1)+":Acquire",1)
            
    def setMethodPath(self,path="/IviumStat/datafiles/"):
        for i in [1]:
            caputS(self.pvStem+"PORT"+str(i)+":MethodDirectory",path)
            
    def setMethodFilename(self,filename):
        """Takes the filename of the method to run (with or without the .imf extension)"""
        if filename[-4:] != ".imf":
            filename = filename+".imf"
        for i in [1]:
            caputS(self.pvStem+"PORT"+str(i)+":MethodFileName",filename)
    
    def setHdfPath(self,path=None):
        """Sets the file path for the HDF file containing the eChem data.
        
        Defaults to the current visit directory /processed/eChem"""
        if path == None:
            path = InterfaceProvider.getPathConstructor().getVisitDirectory() + "/ivium/"
            if not os.path.exists(path): os.makedirs(path)
        caputS(self.pvStem+"HDF"+":FilePath",path)
            
    def setHdfFilename(self,filename):
        """Sets the filename for the HDF file containing the eChem data.
        
        Automatically appends the channel number to the name given"""
        caputS(self.pvStem+"HDF"+":FileName",filename+"_ch{}".format(i))
    
    def primeHdfWriter(self):
        caput(self.pvStem+"HDF"+":Capture",1)
        _waitFor(self.pvStem+"HDF:Capture_RBV",1,checkTime=.1,timeOut=5)
    
    def stopAcquiring(self):
        caput(self.pvStem+"PORT"+str(1)+":Acquire",0)

    def startMethod(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":Acquire",1)
            
    def stopMethod(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":Acquire",0)
        caput(self.pvStem+"HDF"+":Capture",0)
        
    def runMethod(self,methodFilePath):
        self.setMethodMode()
        filename = os.path.basename(methodFilePath)
        filepath = os.path.dirname(methodFilePath)+"/"
        if filename[-4:] != ".imf":
            filename = filename+".imf"
        self.setMethodPath(filepath)
        self.setMethodFilename(filename)
        self.setHdfPath()
        hdfFileName = filename[:-4]
        hdfFileName = hdfFileName+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.setHdfFilename(hdfFileName)
        self.primeHdfWriter()
        self.startMethod()
        print "ivium method {} started".format(filename)

    def setCellMode(self, mode):
        caput(self.pvStem+"PORT"+str(1)+":CellConnection", mode)
        caput(self.pvStem+"PORT"+str(1)+":Apply",1)
            
    def cellOff(self):
        self.setCellMode(0)
        
    def applyCurrent(self, current):
        self.setDirectMode()
        sleep(0.1)
        caput(self.pvStem+"PORT"+str(1)+":AppliedCurrent",current)
        caput(self.pvStem+"PORT"+str(1)+":Apply",1)
        
    def applyVoltage(self, voltage):
        self.setDirectMode()
        sleep(0.1)
        caput(self.pvStem+"PORT"+str(1)+":AppliedPotential",voltage)
        caput(self.pvStem+"PORT"+str(1)+":Apply",1)
        
    def isAcquiring(self):
        return caget(self.pvStem+"PORT"+str(1)+":Acquire") == str(1)
        
ivium = IviumPotentiastat(pvStem="BL07I-EA-IVIUM-01:")

    
def caputS(pv,string):
    ustring = map(ord,string+u"\u0000")
    caput(pv,ustring)
    
def _waitFor(pv,value,checkTime=0.5,timeOut=30,logger=None):
     i = 0
     timeOut = int(float(timeOut) / float(checkTime))
     sleep(float(checkTime))
     while str(caget(pv)) != str(value):
         sleep(float(checkTime))
         i += 1
         if i > timeOut:
             raise Exception("waitFor timed out while waiting for "+ str(pv) + " to change to " + str(value))
    
    
    #eChemMethodCh1_V,eChemMethodCh1_I, eChemMethodCh2_V, eChemMethodCh2_I, eChemMethodCh3_V, eChemMethodCh3_I, eChemMethodCh4_V, eChemMethodCh4_I, eChemMethodCh5_V, eChemMethodCh5_I, eChemMethodCh6_V, eChemMethodCh6_I, eChemMethodCh7_V, eChemMethodCh7_I, eChemMethodCh8_V, eChemMethodCh8_I    


class IviumEpicsMonitor(EpicsMonitor):
        
    def setController(self, controller):
        self.controller = controller
    
    def getPosition(self):
        if not self.isConfigured():
            self.configure()
        if not self.controller.isAcquiring():
            self.controller.setDirectMode()
        return super(IviumEpicsMonitor, self).getPosition()
    
    
    
    
class ScannableIvium(EpicsDeviceClass):
    def __init__(self, name, basePV):
        self.setName(name)
        
        pvAppliedCurrent = '%s:PORT1:AppliedCurrent' %(basePV)
        pvAppliedCurrentRBV  = '%s:PORT1:AppliedCurrent_RBV' %(basePV)
        pvAppliedPotential = '%s:PORT1:AppliedPotential' %(basePV)
        pvAppliedPotentialRBV  = '%s:PORT1:AppliedPotential_RBV' %(basePV)
        pvStartStopAcquire = '%s:PORT1:Acquire' %(basePV)
        pvMeasuredPotentialRBV  = '%s:CHAN1:MeasuredPotential_RBV' %(basePV)
        pvMeasuredCurrentRBV  = '%s:CHAN1:MeasuredCurrent_RBV' %(basePV)
        pvCellMode = '%s:PORT1:CellConnection' %(basePV)
        pvApply = '%s:PORT1:Apply' %(basePV)
        format = '%.6f'
        units = "A"
        self.acquire = CAClient(pvStartStopAcquire)
        self.apply = CAClient(pvApply)
        self.acquire.configure()
        self.apply.configure()
        EpicsDeviceClass.__init__(self,name,pvAppliedPotential,pvAppliedPotential,None,units,format,timeout=None)
        
        self.setInputNames(['Potential'])
        self.setExtraNames(["MeasuredPotential","MeasuredCurrent"])
        
        self.mpr = CAClient(pvMeasuredPotentialRBV)
        self.mpr.configure()
        self.mcr = CAClient(pvMeasuredCurrentRBV)
        self.mcr.configure()
        self.pcb = CAClient(pvAppliedPotentialRBV)
        self.pcb.configure()
        self.cm = CAClient(pvCellMode)
        self.cm.configure()
        self.setDelay(0.5)
        
    def asynchronousMoveTo(self, new_position):
        self.currentposition = new_position;
        self.caput(new_position);
        self.apply.caput(1)
        sleep(1);
        
        
    def atScanStart(self):
        self.acquire.caput(1) 
        sleep(self.delay)
        
    def atScanEnd(self):
        self.acquire.caput(0)
        sleep(self.delay)
        
    def getPosition(self):
        self.acquire.caput(1)
        sleep(1);
        vals = float(self.pcb.caget()),float(self.mpr.caget()),float(self.mcr.caget())
        self.acquire.caput(0)
        return vals
        
    
iviumPotential = IviumEpicsMonitor()
iviumPotential.setController(ivium)
iviumPotential.setPvName("BL07I-EA-IVIUM-01:CHAN1:MeasuredPotential_RBV")
iviumPotential.setName("iviumPotential")

iviumCurrent = IviumEpicsMonitor()
iviumCurrent.setController(ivium)
iviumCurrent.setPvName("BL07I-EA-IVIUM-01:CHAN1:MeasuredCurrent_RBV")
iviumCurrent.setName("iviumCurrent")

iviumRange = EpicsSimpleMbbinary()
iviumRange.setName("iviumRange")
iviumRange.setRecordName("BL07I-EA-IVIUM-01:PORT1:CurrentRange")
iviumRange.configure()
iviumRange.setReadOnly(False)

ivium1 = ScannableIvium("ivium1", "BL07I-EA-IVIUM-01")
    
"""
NOTES ON OPERATION IN DIRECT MODE
1. Changes to applied current/voltage are only taken into account when the PORT is Stopped and Started again
2. When Cell Mode is set to Potential or Current,  is the live Voltage reading and LastCollectionY_RBV is the live Current reading
"""
print "Ivium scripts loaded"
