from gda.device.scannable import ScannableMotionBase
import gda.factory.Finder as Finder
import sys

class Automation(ScannableMotionBase):
    '''Create automation PD that encapsulates and fan-outs control to multiple scannables or pseudo devices.
    
        This pseudo device requies a lookup table object to provide scannable/pseudo device names to which it fans 
        out its request. The lookup table object must be created before the instance creation of this class. The child  
        scannables or pseudo devices must exist in jython's global namespace prior to any method call of this class 
        instance.
        The lookup Table object is described by gda.function.LookupTable class.'''
        
    def __init__(self, name, lutObj='energytable', objType=0, rootNameSpace={}):
        '''Constructor - Only succeed if it find the lookup table, otherwise raise exception.'''
        self.finder=Finder.getInstance()
        self.lut=self.finder.find(lutObj)
        if self.lut==None:
            raise Exception, "Can not find the Lookup Table object"
        self.lut.configure()
        self.rootNameSpace=rootNameSpace
        self.scannableNames=self.lut.getScannableNames()
        self._busy=0
        self.scannables=[self.rootNameSpace[x] for x in self.scannableNames]
        self.setName(name)
        self.setLevel(3)
        self.objType=objType
        self.inputNames=['energy']

    def rawGetPosition(self):
        '''returns the positions of all child scannables.
        det_energy=Automation('det_energy','energytable', DETECTOR)

        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        positions=[]
        try:
            for s in self.scannables:
                if self.objType == 0:
                    try:
                        positions.append(s.getPosition())
                    except:
                        print "Cannot get value from " + s.getName()
                        raise
                elif self.objType == 1:
                    if s.getName() == "energy" or s.getName() == "gap":
                        try:
                            positions.append(s.getPosition())
                        except:
                            print "Cannot get value from " + s.getName()
                            raise
                elif self.objType == 2:
                    if s.getName() == "energy" or s.getName().startswith("alp") or s.getName().startswith("talp"):
                        try:
                            positions.append(s.getPosition())
                        except:
                            print "Cannot get value from " + s.getName()
                            raise
                elif self.objType == 3:
                    if s.getName() == "energy" or s.getName().startswith("pmt") or s.getName().startswith("llim"):
                        try:
                            positions.append(s.getPosition())
                        except:
                            print "Cannot get value from " + s.getName()
                            raise
            return positions
        except:
            print "Error returning position", sys.exc_info()[0]
            raise

    def getExtraNames(self):
        extraNames=[]
        try:
            for s in self.scannables:
                if s.getName() == "energy":
                    continue
                else:
                    if self.objType == 0:
                        extraNames.append(s.getName())
                    elif self.objType == 1:
                        if s.getName() == "gap":
                            extraNames.append(s.getName())
                    elif self.objType == 2:
                        if s.getName().startswith("alp") or s.getName().startswith("talp"):
                            extraNames.append(s.getName())
                    elif self.objType == 3:
                        if s.getName().startswith("pmt") or s.getName().startswith("llim"):
                            extraNames.append(s.getName())
            return extraNames
        except:
            print "Error returning extraNames", sys.exc_info()[0]
            raise

        
    def rawAsynchronousMoveTo(self, new_position):
        '''move every scannables to their corresponding values for this energy.
        
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.'''
        new_position = float(new_position)
        for s in self.scannables:
            if self.objType == 0:
                try:
                    s.asynchronousMoveTo(self.lut.lookupValue(new_position, s.getName()))
                except:
                    print "cannot set " + s.getName() + " to " + str(self.lut.lookupValue(new_position, s.getName()))
                    raise
            elif self.objType == 1:
                if s.getName() == "energy" or s.getName() == "gap":
                    try:
                       # print "move " ,s.getName(), " to ", str(self.lut.lookupValue(new_position, s.getName())) 
                        s.asynchronousMoveTo(self.lut.lookupValue(new_position, s.getName()))
                    except:
                        print "cannot set " + s.getName() + " to " + str(self.lut.lookupValue(new_position, s.getName()))
                        raise                       
            elif self.objType == 2:
                if s.getName().startswith("alp") or s.getName().startswith("talp"):
                    try:
                        s.asynchronousMoveTo(self.lut.lookupValue(new_position, s.getName()))
                    except:
                        print "cannot set " + s.getName() + " to " + str(self.lut.lookupValue(new_position, s.getName()))
                        raise                       
            elif self.objType ==3:
                if s.getName().startswith("pmt") or s.getName().startswith("llim"):
                    try:
                        s.asynchronousMoveTo(self.lut.lookupValue(new_position, s.getName()))
                    except:
                        print "cannot set " + s.getName() + " to " + str(self.lut.lookupValue(new_position, s.getName()))
                        raise                       

                
    def rawIsBusy(self):
        '''checks the busy status of all child scannable.
        
        If and only if all child scannable are done this will be set to False.'''  
        self._busy=0      
        for s in self.scannables:
            if self.objType == 0:
                try:
                    self._busy += s.isBusy()
                except:
                    print s.getName() + " isBusy() throws exception ", sys.exc_info()
                    raise
            elif self.objType == 1:
                if s.getName() == "energy" or s.getName() == "gap":
                    try:
                        self._busy += s.isBusy()
                    except:
                        print s.getName() + " isBusy() throws exception ", sys.exc_info()
                        raise
            elif self.objType == 2:
                if s.getName().startswith("alp") or s.getName().startswith("talp"):
                    try:
                        self._busy += s.isBusy()
                    except:
                        print s.getName() + " isBusy() throws exception ", sys.exc_info()
                        raise
            elif self.objType == 3:
                if s.getName().startswith("pmt") or s.getName().startswith("llim"):
                    try:
                        self._busy += s.isBusy()
                    except:
                        print s.getName() + " isBusy() throws exception ", sys.exc_info()
                        raise
        if self._busy == 0:
            return 0
        else:
            return 1

    def toString(self):
        '''formats what to print to the terminal console.'''
        return self.name + " : " + str(self.getPosition())
    
   


