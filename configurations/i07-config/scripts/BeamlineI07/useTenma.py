from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.configuration.properties import LocalProperties
from gdascripts.installation import isDummy

class TenmaPsu(ScannableMotionBase):
    
    possible_modes = ("I", "V")

    class dummy_single_value_chan():
        
        def __init__(self):
            self.value = 0
        
        def caget(self):
            return self.value
        
        def caput(self, new_value):
            self.value = new_value
    
    def __init__(self, name, pvBase, isDummy):
        self.setName(name)
        self.isDummy = isDummy
        self.setInputNames([name + '_I'])
        self.setExtraNames([name + '_V'])
        self.setOutputFormat(["%.3f", "%.3f"])
        self.epicsSetup(pvBase)
        self.mode = "I"
        self.target = None

    def __del__(self):
        if not self.isDummy :
            self.readVoltageChan.clearup()
            self.readCurrentChan.clearup()
            self.setVoltageChan.clearup()
            self.setCurrentChan.clearup()
                
    def epicsSetup(self, pvBase):
        if isDummy :
            self.readVoltageChan = self.dummy_single_value_chan()
            self.readCurrentChan = self.dummy_single_value_chan()
            self.setVoltageChan = self.readVoltageChan
            self.setCurrentChan = self.readCurrentChan
        else :
            self.readVoltageChan = self.createChannel(pvBase + ':VOLTAGE')
            self.readCurrentChan = self.createChannel(pvBase + ':CURRENT')
            self.setVoltageChan = self.createChannel(pvBase + ':SET_VOLTAGE')
            self.setCurrentChan = self.createChannel(pvBase + ':SET_CURRENT')
        
    def createChannel(self, pv):
        chan = CAClient(pv)
        chan.configure()
        return chan
    
    def getPosition(self):
        """Gets the Voltage and Current"""
        V = self.readVoltageChan.caget()
        I = self.readCurrentChan.caget()
        return I, V

    def isBusy(self):
        """Returns whether the power supply is busy"""
        if self.target == None :
            return False
        elif self.mode == "I" :
            return abs(self.readCurrentChan.caget() - self.target) < 0.01
        elif self.mode == "V" :
            return abs(self.readVoltageChan.caget() - self.target) < 0.01
        else :
            raise ValueError("Mode must be I (current) or V (voltage)")
    
    def setCurrent(self, current):
        self.target = current
        self.setCurrentChan.caput(current)

    def setVoltage(self, voltage):
        self.target = voltage
        self.setVoltageChan.caput(voltage)

    def asynchronousMoveTo(self, new_position):
        """Allows scanning over the Current or Voltage depending on the mode"""
        if self.mode == "I" :
            self.setCurrent(new_position)
        elif self.mode == "V" :
            self.setVoltage(new_position)
            
    def setMode(self, new_mode):
        if self.isBusy() :
            print "Device busy, not setting mode."
            return
        if new_mode not in self.possible_modes :
            raise ValueError("Mode must be I (current) or V (voltage)")
        else :
            self.mode = new_mode
            self.target = None

tenma = TenmaPsu("tenma", "BL07I-EA-TENMA-01", "live"!=LocalProperties.get("gda.mode") )

