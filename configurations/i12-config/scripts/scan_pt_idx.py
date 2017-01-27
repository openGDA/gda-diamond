from gda.device.scannable import PseudoDevice


class ScanPtIdx(PseudoDevice):
    # constructor
    def __init__(self, name, min_inc=0, step_size=1):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%d"])
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
idx=ScanPtIdx('idx', min_inc=1)


#from gda.device.scannable import PseudoDevice
from gda.device.scannable import ScannableUtils

class Facilitator(PseudoDevice):
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



from gda.epics import CAClient 

class ExcludeEarlyFrames(PseudoDevice):
    # constructor
    def __init__(self, name, pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%d"])
        self.pvname=pvname
        self.pvvalue=int(pvvalue)
        self.cli=CAClient(pvname)
        self.backup_pos=None
        self.current_pos=None
        
    def reset(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        if self.backup_pos is not None:
            self.cli.caput(self.backup_pos)
            self.current_pos=self.backup_pos
    
    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.current_pos

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position=False):
        print "rawAsynchronousMoveTo"
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        
        if new_position is not None:
            self.current_pos=int(new_position)
            self.cli.caput(self.cli.current_pos)
        return

    # Returns the status of this Scannable
#    def rawIsBusy(self):
#        #print "hello from rawIsBusy"
#        sleep(1)
#        return

    def isBusy(self):
        return False
    
    def atScanStart(self):
        print "atScanStart"
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        #self.cli.caput(self.pvvalue)           # exclude early frames set to OFF

    def atPointStart(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        self.cli.caput(self.pvvalue)
        #pass
        
    def atPointEnd(self):
        pass
    
    def stop(self):
        self.reset()
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()
    
#earlyFramesINCLUDE=ExcludeEarlyFrames('earlyFramesINCLUDE', pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0)

