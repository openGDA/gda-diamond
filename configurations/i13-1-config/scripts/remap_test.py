'''
filename: RemappedMotor.py

This class uses position compare to determine motor status. It does not use low level Motor Status directly.
Only 3 PVs - set, readback, and stop - are required. No other motor status are handled by this class.
The motor's positional tolerance must be set, that is the same as the retry deadband value of the Motor Record.

Created: 10 Feb 2016

@author: 
'''
print "Running remap_test.py..."

from time import sleep
from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

class RemappedMotor(ScannableMotionBase):
    '''Create a scannable for a single motor'''
    def __init__(self, name, pvinstring, pvoutstring, pvstopstring, pvbusystring, unitstring, formatstring, reverse):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.incli=CAClient(pvinstring)
        self.outcli=CAClient(pvoutstring)
        self.stopcli=CAClient(pvstopstring)
        self.busycli=CAClient(pvbusystring)
        self.reverse = reverse
        
    def atScanStart(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if not self.stopcli.isConfigured():
            self.stopcli.configure()
        if not self.busycli.isConfigured():
            self.busycli.configure()
         
    def rawGetPosition(self):
        try:
            if not self.outcli.isConfigured():
                #print "rawGetPosition: not configured, so needs to be first configured"
                self.outcli.configure()
                output=float(self.outcli.caget())
                eff_ouput = self.remap(output) 
                self.outcli.clearup()
            else:
                #print "rawGetPosition: already configured!"
                output=float(self.outcli.caget())
                #print "output = %f" %(output) 
                eff_output = self.remap(output)
                #print "eff_output = %f" %(eff_output)  
            return eff_output
        except Exception, ex:
            print "Error in rawGetPosition: ", ex
            return float('nan')

    def getTargetPosition(self):
        try:
            if not self.incli.isConfigured():
                #print "getTargetPosition: not configured, so needs to be first configured"
                self.incli.configure()
                target=float(self.incli.caget())
                eff_target = self.remap(target) 
                self.incli.clearup()
            else:
                #print "getTargetPosition: already configured!"
                target=float(self.incli.caget())
                eff_target = self.remap(target) 
            return eff_target
        except Exception, ex:
            print "Error in getTargetPosition: ", ex
            return float('nan')
       
    def rawAsynchronousMoveTo(self,new_position):
        eff_position = self.remap(new_position) 
        if eff_position == self.getTargetPosition():
            #print "rawAsynchronousMoveTo: early return!"
            return
        try:
            if not self.incli.isConfigured():
                #print "rawAsynchronousMoveTo: not configured, so needs to be first configured"
                self.incli.configure()
                self.incli.caput(eff_position)
                self.incli.clearup()
            else:
                #print "rawAsynchronousMoveTo: already configured!"
                self.incli.caput(eff_position)
        except Exception, ex:
            print "Error in rawAsynchronousMoveTo: ", ex

    def isBusy(self):
        try:
            if not self.busycli.isConfigured():
                #print "isBusy: not configured, so needs to be first configured"
                self.busycli.configure()
                isbusy=(not bool(self.busycli.caget()))
                self.busycli.clearup()
            else:
                #print "isBusy: already configured!"
                isbusy=(not bool(self.busycli.caget()))
            return isbusy
        except Exception, ex:
            print "Error in isBusy: ", ex
            return True

    def atScanEnd(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.stopcli.isConfigured():
            self.stopcli.clearup()
        if self.busycli.isConfigured():
            self.busycli.clearup()
            
    def stop(self):
        if not self.stopcli.isConfigured():
            self.stopcli.configure()
            self.stopcli.caput(1)
            self.stopcli.clearup()
        else:
            self.stopcli.caput(1)

    def toString(self):
        return self.name + " : " + str(self.getPosition())

    def remap(self, val):
        eff_val = -val if self.reverse else val
        return eff_val 
    
    def configureAll(self):
        if not self.incli.isConfigured():
            self.incli.configure()
        if not self.outcli.isConfigured():
            self.outcli.configure()
        if not self.stopcli.isConfigured():
            self.stopcli.configure()
        if not self.busycli.isConfigured():
            self.busycli.configure()

    def clearupAll(self):
        if self.incli.isConfigured():
            self.incli.clearup()
        if self.outcli.isConfigured():
            self.outcli.clearup()
        if self.stopcli.isConfigured():
            self.stopcli.clearup()
        if self.busycli.isConfigured():
            self.busycli.clearup()

#def __init__(self, name, pvinstring, pvoutstring, pvstopstring, unitstring, formatstring, reverse)
xgi_x = RemappedMotor(name="xgi_x", pvinstring="BL13J-MO-SMAR-01:GS:Y.VAL", pvoutstring="BL13J-MO-SMAR-01:GS:Y.RBV", pvstopstring="BL13J-MO-SMAR-01:GS:Y.STOP", pvbusystring="BL13J-MO-SMAR-01:GS:Y.DMOV", unitstring="um", formatstring="%.3f", reverse=True)

xgi_y = RemappedMotor(name="xgi_y", pvinstring="BL13J-MO-SMAR-01:GS:Z.VAL", pvoutstring="BL13J-MO-SMAR-01:GS:Z.RBV", pvstopstring="BL13J-MO-SMAR-01:GS:Z.STOP", pvbusystring="BL13J-MO-SMAR-01:GS:Z.DMOV", unitstring="um", formatstring="%.3f", reverse=True)

xgi_z = RemappedMotor(name="xgi_z", pvinstring="BL13J-MO-SMAR-01:GS:X.VAL", pvoutstring="BL13J-MO-SMAR-01:GS:X.RBV", pvstopstring="BL13J-MO-SMAR-01:GS:X.STOP", pvbusystring="BL13J-MO-SMAR-01:GS:X.DMOV", unitstring="um", formatstring="%.3f", reverse=True)


def xgi_configure():
    xgi_x.configureAll()
    xgi_y.configureAll()
    xgi_z.configureAll()
    
def xgi_clearup():
    xgi_x.clearupAll()
    xgi_y.clearupAll()
    xgi_z.clearupAll()


xgi_configure()

print "Finished running remap_test.py - bye!"

