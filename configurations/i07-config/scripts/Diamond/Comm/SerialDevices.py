
from time import sleep;

from gda.epics import CAClient;
from gda.device import DeviceBase

import __main__ as gdamain


class GdaRS232DeviceClass(object):
    def __init__(self, serialController):
        self.serialController=serialController;

    def write(self, sendString):
        self.serialController.sendCommand(sendString);
        
    def read(self):
        reply = self.serialController.getReply()
        return reply;
    
    def writeAndRead(self, sendString):
        self.serialController.sendCommand(sendString);
        sleep(1)
        reply = self.serialController.getReply()
        return reply;
    
    

class EpicsAsynRS232DeviceClass(object):
    BAUDRATE = {'UNKNOWN':0,
                '300' :   1,
                '600':    2,
                '1200':   3,
                '2400':   4,
                '4800':   5,
                '9600':   6,
                '19200':  7,
                '38400':  8,
                '57600':  9,
                '115200':10,
                '230400':11 }
    
    DATABITS = {'UNKNOWN':0,
                '5' :     1,
                '6':      2,
                '7':      3,
                '8':      4 }
    
    PARITY = {'UNKNOWN': 0,
                'None' : 1,
                'Even' : 2,
                'Odd'  : 3 }
    
    FLOWCONTROL = {'UNKNOWN' : 0,
                   'None'    : 1,
                   'Hardware': 2 }

    TRANSFER_MODE = {'WriteRead':0,
                     'Write'    :1,
                     'Read'     :2,
                     'Flush'    :3,
                     'NonIO'    :4 }

    FORMAT = {'ASCII'  :0,
              'Hybrid' :1,
              'Binary' :2,
              'Flush'  :3 }
    
    SEVERITY = {'NO_ALARM':0,
                'MINOR'   :1,
                'MAJOR'   :2,
                'INVALID' :3 }
    
    
    def __init__(self, rootPV):
        self.setupEpics(rootPV);

        portName='ty_50_1'
        baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
        dataBits=EpicsAsynRS232DeviceClass.DATABITS['8'];
        parity=EpicsAsynRS232DeviceClass.PARITY['None'];
        flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None'];
#        self.setPort('', baudRate, dataBits, parity, flowControl, 1);
        
    def __del__(self):
        self.cleanChannel(self.chPort)
        self.cleanChannel(self.chConnect)
        self.cleanChannel(self.chBaudRate)
        self.cleanChannel(self.chDataBits)
        self.cleanChannel(self.chParity)
        self.cleanChannel(self.chFlowControl)

        self.cleanChannel(self.chTimeout)
        self.cleanChannel(self.chTransfer)

        self.cleanChannel(self.chOutputFormat)
        self.cleanChannel(self.chOutputTerminator)
        self.cleanChannel(self.chOutputString)

        self.cleanChannel(self.chInputFormat)
        self.cleanChannel(self.chInputTerminator)
        self.cleanChannel(self.chInputString)

        self.cleanChannel(self.chErrorString)
        self.cleanChannel(self.chStatus)
        self.cleanChannel(self.chSeverity)

        self.cleanChannel(self.chScanMode)
        self.cleanChannel(self.chProcess)

    """ 
    Asyn Driver for RS232:
    
    Port:           BL07I-EA-USER-01:ASYN1.PORT
    Connection:     BL07I-EA-USER-01:ASYN1.PCNCT
    Baud Rate:      BL07I-EA-USER-01:ASYN1.BAUD
    Data Bits:      BL07I-EA-USER-01:ASYN1.DBIT
    Parity:         BL07I-EA-USER-01:ASYN1.PRTY
    Flow Control:   BL07I-EA-USER-01:ASYN1.FCTL
            
    Timeout:    BL07I-EA-USER-01:ASYN1.TMOT
    Transfer:   BL07I-EA-USER-01:ASYN1.TMOD
    
    Output Format:      BL07I-EA-USER-01:ASYN1.OFMT
    Output Terminator:  BL07I-EA-USER-01:ASYN1.OEOS
    Output String:      BL07I-EA-USER-01:ASYN1.AOUT
            
    Input Format:       BL07I-EA-USER-01:ASYN1.IFMT
    Input Terminator:   BL07I-EA-USER-01:ASYN1.IEOS
    Input String:       BL07I-EA-USER-01:ASYN1.TINP
            
    Error String:   BL07I-EA-USER-01:ASYN1.ERRS
    I/O Status:     BL07I-EA-USER-01:ASYN1.STAT
    I/O Severity:   BL07I-EA-USER-01:ASYN1.SEVR
    
    Scan Mode:      BL07I-EA-USER-01:ASYN1.SCAN
    Process:        BL07I-EA-USER-01:ASYN1.PROC 
    """
    def setupEpics(self, rootPV):
        self.chPort=CAClient(rootPV + ".PORT");  self.configChannel(self.chPort);
        self.chConnect=CAClient(rootPV + ".PCNCT");  self.configChannel(self.chConnect);
        self.chBaudRate=CAClient(rootPV + ".BAUD");  self.configChannel(self.chBaudRate);
        self.chDataBits=CAClient(rootPV + ".DBIT");  self.configChannel(self.chDataBits);
        self.chParity=CAClient(rootPV + ".PRTY");  self.configChannel(self.chParity);
        self.chFlowControl=CAClient(rootPV + ".FCTL");  self.configChannel(self.chFlowControl);

        self.chTimeout=CAClient(rootPV + ".TMOT");  self.configChannel(self.chTimeout);
        self.chTransfer=CAClient(rootPV + ".TMOD");  self.configChannel(self.chTransfer);

        self.chOutputFormat=CAClient(rootPV + ".OFMT");  self.configChannel(self.chOutputFormat);
        self.chOutputTerminator=CAClient(rootPV + ".OEOS");  self.configChannel(self.chOutputTerminator);
        self.chOutputString=CAClient(rootPV + ".AOUT");  self.configChannel(self.chOutputString);

        self.chInputFormat=CAClient(rootPV + ".IFMT");  self.configChannel(self.chInputFormat);
        self.chInputTerminator=CAClient(rootPV + ".IEOS");  self.configChannel(self.chInputTerminator);
        self.chInputString=CAClient(rootPV + ".TINP");  self.configChannel(self.chInputString);

        self.chErrorString=CAClient(rootPV + ".ERRS");  self.configChannel(self.chErrorString);
        self.chStatus=CAClient(rootPV + ".STAT");  self.configChannel(self.chStatus);
        self.chSeverity=CAClient(rootPV + ".SEVR");  self.configChannel(self.chSeverity);

        self.chScanMode=CAClient(rootPV + ".SCAN");  self.configChannel(self.chScanMode);
        self.chProcess=CAClient(rootPV + ".PROC");  self.configChannel(self.chProcess);
        
    def configChannel(self, channel):
        if not channel.isConfigured():
            channel.configure();

    def cleanChannel(self, channel):
        if channel.isConfigured():
            channel.clearup();
        
    def setTimeout(self, timeout):
        self.chTimeout.caput(timeout);
        sleep(0.5);
        
    def toCheck(self):
        severity = int( self.chSeverity.caget() );
        if severity == self.SEVERITY["NO_ALARM"] or severity == self.SEVERITY["MINOR"]:
            return True;
        else:
            print "Severity Error:";
            return False;

    def setPort(self, portName, baudRate, dataBits, parity, flowControl, timeout):
        self.chPort.caput(portName);
        self.chBaudRate.caput(baudRate);
        self.chDataBits.caput(dataBits);
        self.chParity.caput(parity);
        self.chFlowControl.caput(flowControl);
        self.chTimeout.caput(timeout);
        self.chScanMode.caput(0); # Set to Passive
        
        self.flush();
        self.toCheck();
        
    def setOutputTerminator(self, terminator):
        self.chOutputTerminator.caput(terminator);
        
    def setInputTerminator(self, terminator):
        self.chInputTerminator.caput(terminator);
        
    def setScanMode(self, newScanMode):
        self.chScanMode.caput(newScanMode);

    def flush(self):
        self.chTransfer.caput( self.TRANSFER_MODE['Flush'] );
        self.chProcess.caput(1);
        sleep(0.5);

    def write(self, sendString):
        self.chTransfer.caput( self.TRANSFER_MODE['Write'] );
        self.chOutputString.caput(sendString);
#        self.chProcess.caput(1);
        sleep(0.5);
        self.toCheck();
            
        
    def read(self):
        self.chTransfer.caput( self.TRANSFER_MODE['Read'] );
#        self.chProcess.caput(1);
        reply=self.chInputString.caget();
        self.toCheck();
        return reply;
        
    def writeAndRead(self, sendString):
        self.chTransfer.caput( self.TRANSFER_MODE['WriteRead'] );
        self.chOutputString.caput(sendString);
#        self.chProcess.caput(1);
        sleep(0.5);
        
        reply=self.chInputString.caget();
        self.toCheck();
        return reply;
        

#from Diamond.Comm.SerialDevices import EpicsAsynRS232DeviceClass, GdaRS232DeviceClass;

#Example port of using EPICS Asyn Driver over RS232
#rootPV = "BL07I-EA-USER-01:ASYN2"
#portName='ty_50_2'
#baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
#dataBits=EpicsAsynRS232DeviceClass.DATABITS['8']
#parity=EpicsAsynRS232DeviceClass.PARITY['None']
#flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None']
#timeout=2;

#port1 = EpicsAsynRS232DeviceClass(rootPV);
#port1.setPort(portName, baudRate, dataBits, parity, flowControl, timeout);
#port1.setOutputTerminator('\r');
#port1.setInputTerminator('\r')
#port1.flush()


#Example port of using the GDA RS232 SerialController
#c=Finder.find("com1")
#sc=Finder.find("sc1")

#sc.setCommandTerminator('')
#sc.setReplyTerminator('\r')
#sc.configure()
#c.flush()
#port2=GdaRS232DeviceClass(sc)


