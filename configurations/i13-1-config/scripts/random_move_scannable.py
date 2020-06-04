"""
File to define a function that allows a scan to be performed that moves a scannable 
alternately through a random sets of positions and its start position

e.g

repscan 10 random_move_scannable.CreateRandomMoveScannable(ix, [(0,10),(20,25)]) 1 ix

The result of this scan is:

Writing data to file (NeXus): /dls/i13-1/data/2012/cm5708-1/2370.nxs
value    step     value
    0       1    23.859
    1       0    0.0000
    2       1    4.6323
    3       0    0.0000
    4       1    1.0548
    5       0    0.0000
    6       1    1.9429
    7       0    0.0000
    8       1    0.87361
    9       0    0.0000
Scan complete.


"""

from gda.device.scannable import ScannableMotionBase
import random


class RandomMoveScannable(ScannableMotionBase):
    """Arguments:
    To create this object:
    RandomMoveScannable( delegateScannable, range)
    where:
    delegateScannable -- the scannable to be moved
    range -- a list of binary tuples expressing the ranges of values to choose from e.g. [(0,10),(20,25)]
    """
    def __init__(self, delegateScannable, range):
        
#        ScannableMotionBase.__init__(self) #do not required as it will be called at end of this __init__ by default
        self.setName(delegateScannable.getName()+"_random")
        self.setInputNames(["step"])
        self.setExtraNames([])
        self.setOutputFormat(["%4d"])
        self.delegateScannable = delegateScannable
        self.range = range
        self.delegateScannableHome = self.delegateScannable.getPosition()
        self.pos = 0
        
    def rawIsBusy(self):
        return self.delegateScannable.isBusy()

    def rawGetPosition(self):
        return self.pos

    def rawAsynchronousMoveTo(self,new_position):
        """
        get next position for scannable in range and move to it
        """
        if self.pos == 0:
            self.pos = 1
            r = random.random()
            rangeToUse = self.range[int(round(float(len(self.range))*r + .5))-1]
            start =rangeToUse[0]
            end = rangeToUse[1]
            val = start + (end-start)*r
            self.delegateScannable.asynchronousMoveTo(val)
        else:
            self.pos = 0
            self.delegateScannable.asynchronousMoveTo(self.delegateScannableHome)
            
        
    def stop(self):
        self.delegateScannable.stop()
        
    def atScanStart(self):
        self.delegateScannableHome = self.delegateScannable.getPosition()


def CreateRandomMoveScannable(delegateScannable, range):
    """Create a scannable 
    Arguments:
    delegateScannable -- the scannable to be moved
    range -- a list of binary tuples expressing the ranges of values to choose from e.g. [(0,10),(20,25)]
    """
    return RandomMoveScannable(delegateScannable, range)