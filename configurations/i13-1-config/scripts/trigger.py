from gda.device.scannable import ScannableMotionBase
from epics_scripts.pv_scannable_utils import caput, caget
import time
from time import sleep
from gda.epics import CAClient 

ca=CAClient("BL13J-EA-ZEBRA-02:SOFT_IN:B0")

class Trigger(ScannableMotionBase):
    # constructor
    def __init__(self, name, width_sec=1, pvname="BL13J-EA-ZEBRA-02:SOFT_IN:B0"):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%d"])
        self.current_pos=0
        self.width_sec=width_sec
        self.start_t=0
        self.cli=CAClient(pvname)
        #self.cli.configure()
    
    def reset(self):
        #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
        if not self.cli.isConfigured():
            print "not configured"
            self.cli.configure()
        self.cli.caput("NO")
        self.current_pos=0

    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.current_pos

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
#        if new_position is not None:
#            self.width_sec=float(new_position)
        return

    # Returns the status of this Scannable
#    def rawIsBusy(self):
#        #print "hello from rawIsBusy"
#        sleep(1)
#        return

    def isBusy(self):
        print "isBusy called"
        #print "hello from isBusy"
        elapsed_t = time.time() - self.start_t
        if elapsed_t < self.width_sec:
            #v=caget("BL13J-EA-ZEBRA-02:SOFT_IN:B0")
            #print "busy: " + `elapsed_t` + ": " + `v`
            return True
        else:
            #print "not busy"
            #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
            if not self.cli.isConfigured():
                print "is busy not configured"
                self.cli.configure()
            else:
                print "isBusy configured"
            #self.cli.caput("NO")
            self.cli.caput(0)
            v=self.cli.caget()
            print "is Busy:" + `v`
            return False
    
    def atScanStart(self):
        if not self.cli.isConfigured():
            self.cli.configure()
            print "at scanStart not configured"
        #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
        #self.cli.caput("NO")
        self.cli.caput(0)
        v=self.cli.caget()
        print "at Scan Start:" + `v`
        self.current_pos=0

    def atPointStart(self):
        #print "at pt start"
        #v1=caget("BL13J-EA-ZEBRA-02:SOFT_IN:B0")
        #print "at ptstart 1:" + `v1`
        #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","Yes")
        if not self.cli.isConfigured():
            self.cli.configure()
            print "at pointStart not configured"
        #self.cli.caput("YES")
        self.cli.caput(1)
        sleep(2)
        v=self.cli.caget()
        print "at pt start:" + `v`
        #sleep(5)
        #v2=caget("BL13J-EA-ZEBRA-02:SOFT_IN:B0")
        #print "at ptstart 2:" + `v2`
        self.current_pos=1
        self.start_t = time.time()
        
    def atPointEnd(self):
        #sleep(1)
        #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
        self.current_pos=0
    
    def stop(self):
        #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
        self.current_pos=0
    
    def atScanEnd(self):
        if not self.cli.isConfigured():
            self.cli.configure()
            print "at scanEnd not configured"
        #self.cli.caput("No")
        self.cli.caput(0)
        caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
        self.current_pos=0
    
    def atCommandFailure(self):
        #caput("BL13J-EA-ZEBRA-02:SOFT_IN:B0","No")
        if not self.cli.isConfigured():
            self.cli.configure()
        self.cli.caput("NO")
        self.current_pos=0
    
    def setWidthSec(self, width_sec):
        self.width_sec=width_sec
        
    
trigz2=Trigger('trigz2', width_sec=0.1, pvname="BL13J-EA-ZEBRA-02:SOFT_IN:B0")
