from time import sleep
from gda.device.scannable import PseudoDevice
#use \r terminator for output (2612SourceMeter) and \n\r for input
#Baud = 9600, bit = 8, bitstop = 1, parity = None, Flow Control = None
#Create Pseudo Device for IsoTech IPS=2010 controlled over Epics Patch Panel
#patch panel RS232 channel 1 (BL06I-EA-USER-01:ASYN1.AOUT)

class Delta(PseudoDevice): 
    def __init__(self, name, channel, Imax, comPort):
        self.setName(name);
        self.setInputNames(['V_'+name])
        self.setExtraNames(['I_'+name])
        self.setOutputFormat(['%3.5f','%3.5f'])
        self.setLevel(6+channel)
        self.channel = channel
        self.Imax = Imax
        self.comPort = comPort
        self.currentPosition = [0, 0]
        self.iambusy = 0
       
        self.initialize()   
 
    def send(self, strCom):
        self.comPort.chOut.caput('CH '+str(self.channel))
        sleep(1)
        self.comPort.chOut.caput(strCom)
        sleep(1)
        return
    
    def initialize(self):
        print "-> initialization of Delta"+str(self.channel)+": Max Current = "+str(self.Imax)+"[A]"
        self.comPort.setParameters(9600,8, 1, "None", "None", "\r","\n\r")
        #setting maximum current 
        strOut = "SO:CU:MA "+str(self.Imax)
        self.send(strOut)
        strOut = "SO:CU "+str(self.Imax)
        self.send(strOut)
        return 

    def turnOn(self):
        return
       
    def turnOff(self):
        self.setVoltage(0)
        self.setCurrent(0)
        return

    def getVoltage(self):
        strOut = 'SO:VO?'
        self.send(strOut)
        voltage=self.comPort.chIn.caget()
        return float(voltage)

    def getCurrent(self):
        strOut = 'SO:CU?'
        self.send(strOut)
        current=self.comPort.chIn.caget()
        return float(current)

    def setVoltage(self, v):
        strOut = 'SO:VO ' + str(v)
        self.send(strOut)
        return

    def setCurrent(self, I):
        strOut = 'SO:CU ' + str(I)
        self.send(strOut)
        return

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self): 
        return [self.getVoltage(), self.getCurrent()]

    def asynchronousMoveTo(self, newVoltage):
        self.setVoltage(newVoltage)
        return

    def isBusy(self):
        return self.iambusy


#example of inintialization:
#exec('[delta1,delta2]=[None,None]')
#com1 = rs232(1,'U1')
#com1.setParameters(9600,8, 1, "None", "None", "\r","\n\r"))
#delta1=Delta('delta1', 1, 0.01, com1) 
#delta2=Delta('delta2', 2, 0.01, com1)
