from time import sleep
from gda.device.scannable import PseudoDevice

#use \r terminator for output (2612SourceMeter) and \n\r for input
#Baud = 9600, bit = 8, bitstop = 1, parity = None, Flow Control = None
#Create Pseudo Device for IsoTech IPS=2010 controlled over Epics Patch Panel
#patch panel RS232 channel 1 (BL06I-EA-USER-01:ASYN1.AOUT)
 
class Lakeshore331_class(PseudoDevice): 
    def __init__(self, name, comPort):
        self.setName(name);
        self.setInputNames(['temp[K]'])
        self.setOutputFormat(['%3.2f'])
        self.setLevel(9)
        self.comPort = comPort
        
        self.iambusy = 0
        self.tempChannel = 'A'
       
        self.initialize() 
        self.currentPosition = self.getPosition()  
 
    def send(self, commandStr):
        self.comPort.chOut.caput(commandStr)
        sleep(0.4)
        return

    def read(self):
        return self.comPort.chIn.caget()
    
    def initialize(self):
        self.send('BAUD 2')
        sleep(1)
        self.send('INTYPE B,2,0')  #set input sensor pt100/250, no compensation on input B
        sleep(1)
        self.send('PID 1,22,22,0')   #set PID parameters
        sleep(1)
        self.send('CMODE 1,3')  #set loop 1 to open loop
        sleep(1)
        self.send('SETP 1,0')
        sleep(1)   
        self.send('RAMP 1,0,5')  #set the ramp off and to 5Kelvin/minute
        sleep(1)
        self.send('RANGE 1')   #set heater range
        sleep(1)
        strOut = 'CSET 1,'+self.tempChannel+',1,1,1'
        self.send(strOut)   #set the loop one units and turn power on

        print "-> initialization of Lakeshore 331S completed"
        #self.comPort.setParameters(9600,7, 1, "Odd", "None", "\r\n","\r\n")

        return 

    def getSetPoint(self):
        strOut = 'SETP? 1'
        self.send(strOut)
        return float(self.read())

    def getHeaterPower(self):
        strOut = 'HTR?'
        self.send(strOut)
        return float(self.read())
    
    def heaterOn(self):
        self.send('RANGE 1')
        return

    def heaterOff(self):
        self.send('RANGE 0')
        return

    def openLoop(self):
        self.send('CMODE 1,3')
        strOut = 'CSET 1,'+self.tempChannel+',1,0,1'
        self.send(strOut) 

    def closedLoop(self):
        self.send('CMODE 1,1')
        strOut = 'CSET 1,'+self.tempChannel+',1,1,1'
        self.send(strOut) 
    
    def rampOn(self):
        self.send('RAMP 1,1,5')
        
    def rampOff(self):
        self.send('RAMP 1,0,5')

    def setHeaterPower(self, heaterPower):
        strOut = 'MOUT 1,'+str(heaterPower)
        self.send(strOut)
        return

    def atScanStart(self):
        return

    def atScanEnd(self):
        return
    
    def getTemperature(self):
        strOut = 'KRDG? ' + self.tempChannel
        self.send(strOut)
        return self.read()
    
    def setTemperature(self, setpKelvin):
        strOut = 'SETP 1,'+str(setpKelvin)
        self.send(strOut)
        return

    def getPosition(self):
        strOut = 'KRDG? ' + self.tempChannel
        self.send(strOut)
        self.currentPosition = self.read()
        return self.currentPosition

    def asynchronousMoveTo(self, setpKelvin):
        strOut = 'SETP 1,'+str(setpKelvin)
        self.send(strOut)
        return

    def isBusy(self):
        return self.iambusy

class LakeshoreTemperature_class(PseudoDevice): 
    def __init__(self, name, lakeshore):
        self.setName(name);
        self.setInputNames(['temperature[k]'])
        self.setOutputFormat(['%3.2f'])
        self.setLevel(9)
        self.lakeshore = lakeshore
        self.currentPosition = self.lakeshore.getTemperature()
        
    def getPosition(self):
        self.currentPosition = self.lakeshore.getTemperature()
        return self.currentPosition

    def asynchronousMoveTo(self, setpKelvin):
        self.lakeshore.setTemperature(setpKelvin)
        return

    def isBusy(self):
        return False

class LakeshoreHeaterOut_class(PseudoDevice): 
    def __init__(self, name, lakeshore):
        self.setName(name);
        self.setInputNames(['Percent'])
        self.setOutputFormat(['%3.2f'])
        self.setLevel(9)
        self.lakeshore = lakeshore
        self.currentPosition = self.lakeshore.getHeaterPower()
        
    def getPosition(self):
        self.currentPosition = self.lakeshore.getHeaterPower()
        return self.currentPosition

    def asynchronousMoveTo(self, setpKelvin):
        return

    def isBusy(self):
        return False
    
class LakeshoreSetPoint_class(PseudoDevice): 
    def __init__(self, name, lakeshore):
        self.setName(name);
        self.setInputNames(['setPoint[k]'])
        self.setOutputFormat(['%3.2f'])
        self.setLevel(9)
        self.lakeshore = lakeshore
        self.currentPosition = self.lakeshore.getSetPoint()
        
    def getPosition(self):
        self.currentPosition = self.lakeshore.getSetPoint()
        return self.currentPosition

    def asynchronousMoveTo(self, setpKelvin):
        return

    def isBusy(self):
        return False
#example of inintialization:

