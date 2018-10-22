from time import sleep
from gda.epics import CAClient
# this is to support 2 branches of the beamline
class rs232:
    def __init__(self,port,panel):
        self.port = port
        panelDict = {'U1' : 'I', 'U2' : 'J'}
        if panel.upper() not in ['U1', 'U2', 'I', 'J']:
            print "-> patch panel choice is invalid: allowed values are U1 or U2"
            print "-> U1 panel selected as default."
            self.panel = 'U1' 
        else:
            self.panel = panel 
        panelStr = panelDict[panel.upper()] 
        rootComStr =  "BL06"+panelStr+"-EA-USER-01:ASYN"
        self.addrStr = rootComStr+"%1u." % self.port
        pvIn = rootComStr+"%1u.TINP" % self.port
        pvOut = rootComStr+"%1u.AOUT" % self.port
        self.chIn=CAClient(pvIn)
        self.chIn.configure()
        self.chOut=CAClient(pvOut)
        self.chOut.configure()

        self.baudList = ["Unknown","300","600","1200","2400","4800","9600"]
        self.baudList += ["19200","38400","57600","115200","230400"]
        self.bitList = ["Unknown","5","6","7","8"]
        self.stopList = ["Unknown","1","2"]
        self.parityList = ["Unknown","None", "Even", "Odd"]
        self.flowList = ["Unknown","None", "Hardware"]
        
        self.getParameters()
        self.report()
        
    def initialize(self):
        strOut =  "-> setting Serial port %u " % self.port + "of panel %s" %self.panel
        print strOut
        self.chOut.caput(self.addrStr+"BAUD", str(self.baud))
        sleep(0.5)
        self.chOut.caput(self.addrStr+"DBIT", str(self.bit))
        sleep(0.5)
        self.chOut.caput(self.addrStr+"SBIT", str(self.stop))
        sleep(0.5)
        self.chOut.caput(self.addrStr+"PRTY", str(self.parity))
        sleep(0.5)
        self.chOut.caput(self.addrStr+"FCTL", self.flow)
        sleep(0.5)
        self.chOut.caput(self.addrStr+"OEOS",self.outTerm)
        sleep(0.5)
        self.chOut.caput(self.addrStr+"IEOS",self.inTerm)
        self.report()
    
    def setParameters(self, baud, bit, stop, parity, flow, outTermination, inTermination):
        #example: com.setParameters(4800,8, 1, "None", "None", "\r","\r\n")
        if str(baud) in self.baudList:
            self.baud = str(baud)
        else: 
            self.baud="Unknown"
        if str(bit) in self.bitList:
            self.bit = str(bit)
        else: 
            self.bit = "Unknown"
        if str(stop) in self.stopList:
            self.stop = str(stop)
        else: 
            self.stop = "Unknown"
        if parity in self.parityList:
            self.parity = str(parity)
        else: 
            self.parity = "Unknown"
        if flow in self.flowList: 
            self.flow = str(flow)
        else: 
            self.flow = "Unknown"
        self.outTerm = outTermination
        self.inTerm = inTermination
        self.initialize()
      
    def setBaud(self,baud):
        if str(baud) in self.baudList:
            self.baud = str(baud)
        else: 
            self.baud = "Unknown"
        self.initialize()
        
    def setDataBits(self,bit):
        if str(bit) in self.bitList:
            self.bit = str(bit)
        else: 
            self.bit = "Unknown"
        self.initialize()

    def setStop(self, stop):
        if str(stop) in self.stopList:
            self.stop = str(stop)
        else: 
            self.stop = "Unknown"
        self.initialize()

    def setInTerminator(self, inTerm):
        self.stop = str(inTerm)
        self.initialize()
        
    def getParameters(self):
        self.baud = self.baudList[int(self.chIn.caget(self.addrStr+"BAUD"))]
        self.bit = self.bitList[int(self.chIn.caget(self.addrStr+"DBIT"))]
        self.stop = self.stopList[int(self.chIn.caget(self.addrStr+"SBIT"))]
        self.parity = self.parityList[int(self.chIn.caget(self.addrStr+"PRTY"))]
        self.flow = self.flowList[int(self.chIn.caget(self.addrStr+"FCTL"))]
        self.outTerm = str(self.chIn.caget(self.addrStr+"OEOS"))
        self.inTerm = str(self.chIn.caget(self.addrStr+"IEOS"))
    
    def report(self):
        self.getParameters()
        outStr = "Rs232 port %d " %self.port + "of patch panel %s current configuration:" %self.panel
        print outStr
        strOut = "  Baud: %s, " %self.baud +  "Bit: %s," %self.bit + " Stop bit: %s," %self.stop
        strOut +=" Parity: %s," %self.parity + " Flow: %s" %self.flow
        print strOut
        print "  Output terminator: %s," %self.outTerm+ " Input terminator: %s" %self.inTerm
    
    def send(self, strCom):
        self.chOut.caput(strCom)
        sleep(0.05)
        return
    
    def read(self):
        strCom = self.chIn.caget(self.addrStr+"TINP")
        return strCom
      
 
