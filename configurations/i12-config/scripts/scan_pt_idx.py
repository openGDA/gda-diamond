from gda.device.scannable import ScannableMotionBase


class ScanPtIdx(ScannableMotionBase):
    # constructor
    def __init__(self, name, min_inc=0, step_size=1):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat([])
        self.min_inc=min_inc
        self.step_size=step_size
        self.current_idx=min_inc
    
    def reset(self):
        self.current_idx = self.min_inc
    
    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.current_idx

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return
        
    def atPointStart(self):
        pass
        
    def atPointEnd(self):
        self.current_idx += self.step_size
    
    def stop(self):
        pass
    
    def atScanEnd(self):
        self.current_idx=self.min_inc
    
    def atCommandFailure(self):
        self.current_idx=self.min_inc
    
zidx=ScanPtIdx('zidx')


#from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableUtils

class Facilitator(ScannableMotionBase):
    def __init__(self, name, cmdTemplate = [("pco.setCollectionTime(%s)", "self.reqdPos"), ("pco.getController().armCamera()", None)], cmdPreCondition=[("%s > 0", "self.reqdPos")], noopPos=-1):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.noopPos = noopPos
        self.currPos = self.noopPos     # this template scannable represents a single number
        self.reqdPos = self.currPos
        self.iambusy = 0                # flag to hold the status of the scannable
        self.cmdTemplate = [("pco.setCollectionTime(%s)", "self.reqdPos"), ("pco.getController().armCamera()", None)]
        self.cmdPreCondition = [("%s > 0", "self.reqdPos"), ("%s != self.noopPos", "self.reqdPos")]
    
    def reset(self):
        self.currPos = self.noopPos
        self.reqdPos = self.currPos
        self.iambusy = 0
    
    def atPointStart(self):
        if self.reqdPos != self.noopPos and self.reqdPos != self.currPos:
            cond_all = True
            for p in self.cmdPreCondition:
                if p[1] is not None:
                    cond = "p[0] %p[1]"
                    print cond
                    cond = eval(cond)
                else:
                    cond = p[0]
                print cond
                cond_all = cond_all and eval(cond)
            if cond_all:
                for c in self.cmdTemplate:
                    if c[1] is not None:
                        cmd = "c[0] %c[1]"
                        print cmd
                        cmd = eval(cmd)
                    else:
                        cmd = c[0]
                    print cmd
                    exec(cmd)
                self.currPos = self.reqdPos
                print "atPointStart: done - at currPos = " + `self.currPos`
            else:
                print "Command pre-conditions not satisfied for reqdPos = " + `self.reqdPos` + " (currPos = " + `self.currPos`+")"
        else:
            print "No-op for reqdPos = " + `self.reqdPos` + " as currPos = " + `self.currPos`
    
    def getPosition(self):
        """returns the value this scannable represents."""
        return self.currPos
    
    def asynchronousMoveTo(self, newPos):
        """Performs the operation this Scannable represents."""
        self.iambusy = 1
        self.reqdPos = newPos
        self.iambusy = 0
    
    def isBusy(self):
        """Returns the status of this Scannable."""
        return self.iambusy
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()
        
    def stop(self):
        self.reset()

fussy=Facilitator('fussy')



