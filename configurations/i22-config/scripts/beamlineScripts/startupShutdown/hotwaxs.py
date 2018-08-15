class Hotwaxs(gda.device.scannable.PseudoDevice):

    def __init__(self):
        self.name = "hotwaxs"
        self.setInputNames(["cathodes"])
        self.setExtraNames(["window", "side" , "drift"])
        self.setOutputFormat(["%5.3f", "%5.3f", "%5.3f" , "%5.3f"])
        self.PVname = "BL22I-EA-HV-01:"
        self.cathodes = HotWaxsVoltages( self.PVname , "cathodes" , 0 )
        self.window = HotWaxsVoltages( self.PVname , "window" , 1 )
        self.side = HotWaxsVoltages( self.PVname , "side" , 2 )
        self.drift = HotWaxsVoltages( self.PVname , "drift" , 3 )

    def isBusy(self):
        return 0

    def getPosition(self):
        return [ self.cathodes.getPosition() , self.window.getPosition() , self.side.getPosition() , self.drift.getPosition() ] 

    def asynchronousMoveTo(self,X):
        if ( str(X) == "on" or str(X) == "off"):
            if ( str(X) == "on"):
                self.on()
            if ( str(X) == "off"):
                self.off()
            return
        return "Choices are on or off"

    def on(self):
        if ( self.cathodes.isChannelEnabled() == 1 or self.window.isChannelEnabled() == 1 or self.side.isChannelEnabled() == 1 or self.drift.isChannelEnabled()==1 ):
            print "One or more channels are off. Turn the power supply on"
            return
        print "Set HOTWAXS high voltages ON"
        self.cathodes.on()
        self.window.on()
        self.side.on()
        self.drift.on()
        
        pos self.cathodes 200
        self.waitForVoltage(self.cathodes , 200)
        pos self.window 600
        self.waitForVoltage(self.window , 600)
        pos self.side 600
        self.waitForVoltage(self.side , 600)
        pos self.drift 1200
        self.waitForVoltage(self.drift , 1200)
        
        pos self.cathodes 400
        self.waitForVoltage(self.cathodes , 400)
        pos self.window 1200
        self.waitForVoltage(self.window , 1200)
        pos self.side 1200
        self.waitForVoltage(self.side , 1200)
        pos self.drift 2400
        self.waitForVoltage(self.drift , 2400)

        pos self.cathodes 470
        self.waitForVoltage(self.cathodes , 470)
        pos self.window 1500
        self.waitForVoltage(self.window , 1500)
        pos self.side 1500
        self.waitForVoltage(self.side , 1500)
        pos self.drift 3000
        self.waitForVoltage(self.drift , 3000)
        
        return

    def waitForVoltage(self , channel , voltage):
        position = float(channel.getPosition())
        while( abs(position-float(voltage)) > 5 ):
            sleep(1)
            position = float(channel.getPosition())
        
    def off(self):
        if ( self.cathodes.isChannelEnabled() == 0 ):
            pos self.cathodes 0.0
            self.cathodes.off()
            
        if (self.window.isChannelEnabled() == 0):
            pos self.window 0.0
            self.window.off()
            
        if ( self.side.isChannelEnabled() == 0):
            pos self.side 0.0
            self.side.off()
        
        if ( self.drift.isChannelEnabled() == 0):
            pos self.drift 0.0
            self.drift.off()
        self.waitForVoltage(self.cathodes , 0)
        self.waitForVoltage(self.window , 0)
        self.waitForVoltage(self.side , 0)
        self.waitForVoltage(self.drift , 0)    
        return

    def isOn(self):
        return (self.cathodes.isChannelEnabled() and self.window.isChannelEnabled() and self.side.isChannelEnabled() and self.drift.isChannelEnabled())
    
class HotWaxsVoltages(gda.device.scannable.PseudoDevice):
    
    def __init__(self , pvName , name , channel):
        self.name = name
        self.pvName = pvName
        self.pvOn = self.pvName+"ON"+str(channel)
        self.pvSet = self.pvName+"VSET"+str(channel)
        self.readout = self.pvName+"VMON"+str(channel)+":RBV"
        self.channelOn = self.pvName+"STAT"+str(channel)+":RBV.B0"
        self.rampUp = self.pvName+"STAT"+str(channel)+":RBV.B1"
        self.rampDown = self.pvName+"STAT"+str(channel)+":RBV.B2"
        self.pvTripped = self.pvName+"STAT"+str(channel)+":RBV.B7"
        self.pvEnabled = self.pvName+"STAT"+str(channel)+":RBV.BA"

    def isBusy(self):
        return 0

    def getPosition(self):
        position = "OFF"
        if ( self.isChannelEnabled() == 0 ):
            position = caget(self.readout)
        return position 

    def asynchronousMoveTo(self,X):
        if ( self.isChannelEnabled() == 1 ):
            print self.name+" OFF.Turn power supply on"
            return
        self.on()
        caput(self.pvSet , X)
        return

    def isChannelEnabled(self):
        return int(caget(self.pvEnabled))
    
    def off(self):
            caput ( self.pvOn , 0)
            return

    def on(self):
            caput ( self.pvOn , 1)
            return

hw = Hotwaxs()