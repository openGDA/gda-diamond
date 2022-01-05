
from gda.device.scannable import ScannableMotionBase, ScannableBase
from gda.device import Scannable

from gda.scan import ConcurrentScan
from gda.scan import ScanBase, ScanPositionProviderFactory, ScanPositionProvider
from gda.jython.commands.GeneralCommands import alias

import java.lang.InterruptedException #@UnresolvedImport

class MyScanClass(object):
    def __init__(self):
        self.finalPosition=None;
        self.scan=None;
        
    def __call__(self, *args):
        
#        newArgs=args;
        newArgs=self.parseArgs(args);

        #To create the scan
        self.scan = ConcurrentScan(newArgs)

        #To run the scan
        try:
            self.scan.runScan()
        except java.lang.InterruptedException, e:
            if not self.scan.wasScanExplicitlyHalted():
                raise e
            else:
                # Keep going if the scan was stopped manually
                print ("=== Scan stopped early by user: ")
        finally:
            pass;
        
        # Possibly return to start positions
        if self.finalPosition:
            pass
#            self.returnToInitialPositions(initialPositions)
    

    def parseArgs(self, args):
        """ To change the sections with range and steps into a single individual position list
        eg: [[x, (1, 2, 3, 3.5, 4, 4.5, 5), z] = parseArgs([x, (R1, R2, Ri, ...), z])
        where Ri=[start, stop, step]
        """
        newArgs=[]
        if len(args) == 0:
            raise SyntaxError(self.__doc__)
        # start off with the first arg which must be a scannable
        # the first argument should be a scannable else a syntax error
        if isScannable(args[0]) == False:
            raise Exception("First argument to scan command must be a scannable")
        
        newArgs.append(args[0]);
        
        for a in args[1:]:
            if self.isRegionTuple(a):
                newScanRegion = ScanPositionProviderFactory.createFromRegion(list(a))
                newArgs.append(newScanRegion)
            else:
                newArgs.append(a)
        
        return newArgs;
        
    #True if rp is ([X,X,X], [Y,Y,Y], ... [Z,Z,Z])
    def isRegionTuple(self, rp):
        result = True;

        if not isinstance(rp, tuple):
            result = False;
        else:
            for stp in rp:
                if not isinstance(stp, list):
                    result=False;
                    break;
                elif len(stp) != 3:
                        result = False;
                        break;
                    
        return result;

def isScannable(obj):
    return isinstance(obj, (ScannableMotionBase, ScannableBase, Scannable))

#Usage
myscan=MyScanClass()
alias('myscan');

#The following three ways to run the scan command:
#myscan(*[testMotor1 0 10 1 dummyCounter1 0.1])
#myscan(testMotor1, 0, 10, 1, dummyCounter1, 0.1)
#myscan testMotor1 0 10 1 dummyCounter1 0.1

#myscan testMotor1 0 10 1 dummyCounter1 0.1

#myscan testMotor1 ([0, 5, 1], [6,10,0.1], [10,15,1]) dummyCounter1 0.1

