
import math;
from gda.device.scannable import ScannableMotionBase, ScannableBase
from gda.device import Scannable

from gda.scan import ConcurrentScan
from gda.scan import ScanPositionProviderFactory
from gda.jython.commands.GeneralCommands import alias

import java.lang.InterruptedException #@UnresolvedImport

class PowerSeriesScanClass(object):
    def __init__(self):
        self.finalPosition=None;
        self.scan=None;
        self.minimalNoneZero=0.1;
        
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
        if self.isScannable(args[0]) == False:
            raise Exception("First argument to scan command must be a scannable")
        
        if len(args) == False:
            raise Exception("First argument to scan command must be a scannable")
        
        scanDict=self.mapArgs(args);
        for k, v in scanDict.iteritems():
            if len(v) == 3:
                vp=self.getPowerSeries(*v);
                newArgs.append(k);
                newArgs.append(vp);
            else:
                newArgs.append(k);
                newArgs.extend(v);
        
        return newArgs;

    def mapArgs(self, args):
        scanDict=dict();
            
        for a in (args):
            if self.isScannable(a): #new entry in the scanDict
                newDevice=a;
                scanDict[newDevice]=[];
            else:
                scanDict[newDevice].append(a);
        return scanDict;

    def getPowerSeries(self, start, end, q):
        
        #To make sure there is no zero start/end
        if start == 0:
                start=self.minimalNoneZero * cmp(end, 0);
        if end == 0:
            end=self.minimalNoneZero* cmp(start, 0);
        q=abs(q);

        if start == end:
            raise Exception("Start and End messed up!");
        
        if start>0 and end>0:
            s=self.powerSeries( start, end, q*cmp(end, start) );
        elif start<0 and end<0:
            s=self.powerSeries( start, end, -q*cmp(end, start) );
        elif start<0 and end>0:
#                print("-10, 5");
                s=self.powerSeries( start, -self.minimalNoneZero, -q );
                s2=self.powerSeries( self.minimalNoneZero, end, q );
                s.extend(s2) 
        elif start>0 and end<0:
#                print("10, -5");
                s=self.powerSeries( start, self.minimalNoneZero, -q );
                s2=self.powerSeries( -self.minimalNoneZero, end, q );
                s.extend(s2) 
        else:
            print("Confused?! ")
            raise Exception("Start and End messed up!")
            
        return tuple(s);
    
    def powerSeries(self, start, end, q):
        a0=float(start);
        a1=float(end);
#        if a0 < self.minimalNoneZero:
#            print("Start/End position should be above zero. Use default minimum value instead")
#            a0=self.minimalNoneZero;
        n=int( math.log(a1/a0)/math.log(1+q) ) + 1; #Number of points
        s=[a0*pow(1+q, i) for i in range(n)];
        s.append(a1);
        return s;
        

    def isScannable(self, obj):
        return isinstance(obj, (ScannableMotionBase, ScannableBase, Scannable))

#Usage
#iscan=PowerSeriesScanClass()
#alias('iscan');
