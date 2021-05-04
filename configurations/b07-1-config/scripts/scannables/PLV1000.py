'''
Created on Apr 14, 2021

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class PLV1000_Class(ScannableMotionBase):
    '''
    scannable for PLV1000 controller
    '''


    def __init__(self, name, root_pv_name):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%f"])
        self.setcli=CAClient(root_pv_name +":Voltage")
        self.readCli = CAClient(root_pv_name +":Voltage_RBV")
        self.oncli=CAClient(root_pv_name +":On.PROC")
        self.offCli = CAClient(root_pv_name +":OffRamp.PROC")

    def atScanStart(self):
        if not self.setcli.isConfigured():
            self.setcli.configure()
        if not self.readCli.isConfigured():
            self.readCli.configure()
        if not self.oncli.isConfigured():
            self.oncli.configure()
        if not self.offCli.isConfigured():
            self.offCli.configure()
         
    def rawGetPosition(self):
        try:
            if not self.readCli.isConfigured():
                self.readCli.configure()
                output=float(self.readCli.caget())
                self.readCli.clearup()
            else:
                output=float(self.readCli.caget())
            return output
        except:
            print("Error returning current position")
            return 0
    
    def rawAsynchronousMoveTo(self,new_position):
        new_pos = float(new_position)
        if new_pos < 0 or new_pos > 1000:
            raise ValueError("Input is outside permitted range [0, 1000]!")
        try:
            if not self.setcli.isConfigured():
                self.setcli.configure()
                self.setcli.caput(new_position)
                self.setcli.clearup()
            else:
                self.setcli.caput(new_position)
        except:
            print("error moving to position")

    def rawIsBusy(self):
        return False

    def on(self):
        try:
            if not self.oncli.isConfigured():
                self.oncli.configure()
                self.oncli.caput(1)
                self.oncli.clearup()
            else:
                self.oncli.caput(1)
        except:
            print("error set to On position")

    def off(self):
        try:
            if not self.offcli.isConfigured():
                self.offcli.configure()
                self.offcli.caput(1)
                self.offcli.clearup()
            else:
                self.offcli.caput(1)
        except:
            print("error set to Off position")

    def atScanEnd(self):
        if self.setcli.isConfigured():
            self.setcli.clearup()
        if self.readCli.isConfigured():
            self.readCli.clearup()
        if self.oncli.isConfigured():
            self.oncli.clearup()
        if self.offCli.isConfigured():
            self.offCli.clearup()
            
    def toFormattedString(self):
        return "%s: %s" % (self.getName(), self.getPosition())
    
plv1 = PLV1000_Class("plv1", "BL07C-EA-PLV-01")
plv2 = PLV1000_Class("plv2", "BL07C-EA-PLV-02")
        