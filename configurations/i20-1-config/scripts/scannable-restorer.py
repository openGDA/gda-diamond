from gda.device.scannable import ScannableBase
from org.apache.commons.math3.stat.correlation import StorelessBivariateCovariance
from __builtin__ import True, None

class ScannableRestorer(ScannableBase):
    """
Scannable that can be added to a scan to allow the positions of several scannables to
be stored at the beginning of a scan and restored at the end.
For ScannableMotor objects, the speed is also recorded and restored.

Methods for controlling which scannables are stored :
    addScannable(scn) - add a scannable to the list of scannables to be stored/restored
    removeScannable(scn) - remove a scannable from the list
    getScannables() - get list of all the scannables
    clearScannables() - clear the list of scannables
    
Methods for storing, applying positions and speeds :
    storeScannableParams() - store the positions and speeds of the scannables in the list
    restoreScannableParams() - apply the stored positions and speeds to the scannables
    showStoredParameters() - show the stored parameters for each scannable

Other settings :
    setStoreAtScanStart(store) - set to true to store position and speed at start of a scan
    setRestoreAtScanStart(store) - set to true to restore parameters at the end of a scan

imh 25/2/2022
 
    """

    def __init__(self, name):
        self.name = name
        self.setOutputFormat({});
        self.setInputNames({});
        
        self.scannables = []
        self.scannableParams = {} # dictionary from scannable name to parameter value(s).
        
        self.storeAtScanStart = True
        self.restoreAtScanEnd = True

    def setStoreAtScanStart(self, store):
        self.storeAtScanStart = store
    
    def isStoreAtScanStart(self):
        return self.storeAtScanStart
    
    def setRestoreAtScanEnd(self, store):
        self.restoreAtScanEnd = store
    
    def isRestoreAtScanEnd(self):
        return self.restoreAtScanEnd
    
    def atScanStart(self):
        if self.storeAtScanStart :
            self.storeScannableParams()
        
    def atScanEnd(self):
        if self.restoreAtScanEnd :
            self.restoreScannableParams()
        
    def atCommandFailure(self) :
        self.atScanEnd()

    def stop(self) : 
        self.atScanEnd()
    
    def addScannable(self, scn):
        if self.scannables.__contains__(scn) == False :
            self.scannables.append(scn)
    
    def addScannableParameters(self, scn, position=None, speed=None) :
        self.addScannable(scn)
        scnName = scn.getName()
        vals = [None, None]
        if self.scannableParams.has_key(scnName) :
            vals = self.scannableParams.get(scnName)
        
        if position != None :
            vals[0] = position
        if speed != None :
            vals[1] = speed 
        
        print "Storing parameters for %s : position = %s, speed =  %s"%(scnName, position, speed)
        self.scannableParams[scnName] = vals


    def removeScannable(self, scn) :
        self.scannables.remove(scn)
     
    def getScannables(self):
        return self.scannables
    
    def clearScannables(self):
        self.scannables = []
           
    def storeScannableParams(self):
        self.scannableParams = {}
        for scn in self.scannables :
            print "Storing parameters for %s"%(scn.getName())
            self.scannableParams[scn.getName()] = self.getParameters(scn)
    
    # Return parameters for a scannable :
    # For a Scannable motor - tuple of position and speed.
    # All other scannables - position
    def getParameters(self, scn):
        if isinstance(scn, ScannableMotion) :
            return [scn.getPosition(), scn.getSpeed()]
        else : 
            return [scn.getPosition(), None]

    def restoreScannableParams(self) :
        for scn in self.scannables :
            print "Restoring parameters for %s"%(scn.getName())
            self.restoreParams(scn)
    
  
    def restoreParams(self, scn) :
        paramIsPresent = lambda arr, index : len(arr) > index and arr[index] != None
            
        if self.scannableParams.has_key(scn.getName()) == False :
            print "Cannot restore position for %s - no stored parameters for this scannable"%(scn.getName())
            return 
        
        params = self.scannableParams[scn.getName()]
        # Restore the speed first
        if paramIsPresent(params, 1) :
            print "Setting speed to %.3f"%(params[1])
            scn.setSpeed(params[1])
            
        # Restore the position
        if paramIsPresent(params, 0) :
            print "Setting position to %.4f"%(params[0])
            scn.moveTo(params[0])

    def showStoredParameters(self):
        for item in self.scannableParams.items() :
            print "%s : %s"%(item[0], item[1])
        
    
#scannableRestorer = ScannableRestorer("scannableRestorer")
#scannableRestorer.addScannable(turbo_slit_x)
#scannableRestorer.addScannable(sample_x)
#scannableRestorer.addScannable(sample_y)
