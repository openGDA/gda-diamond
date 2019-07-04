from time import sleep
from java import lang

from gda.factory import Finder
from gda.data import NumTracker

#New style Pseudo devices use gda.device.scannable.PseudoDevice 
from gda.device.scannable import PseudoDevice
#New style Pseudo detectors use gda.device.detector.PseudoDetector 
from gda.device.detector import PseudoDetector

#Old style Pseudo devices use gda.device.scannable.ScannableBase
#from gda.device.scannable import ScannableBase
#from gda.device import Scannable

from temp.SocketDevice import SockteDeviceClass;

#The Class for creating a socket-based Psuedo Device
#class CameraSockteDeviceClass(ScannableBase):
class ClassixCameraDeviceClass(SockteDeviceClass, PseudoDetector):
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        self.setInputNames([]);
        self.setExtraNames([name]);
#        self.Units=[strUnit];
        self.setLevel(7);
        
        #New style Python class with super() to invoke base class constructor
#        super(CameraSockteDeviceClass, self).__init__(hostName, hostPort);
        #Old style Python class to invoke base class constructor
        SockteDeviceClass.__init__(self, hostName, hostPort);
        
        self.exposureTime = 1;

    def quit(self):
        while self.checkStatus() != 'READY':
            sleep(1);
        
        reply = self.sendAndReply('QUIT');
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'OK':
            print "Error with QUIT: " + reply;
        print "QUIT command successfully sent out";
        return;
    
    def save(self, startPos, stopPos, stepSize):
        while self.checkStatus() != 'READY':
            sleep(1);
            
        scanNumber=self.getScanNumber();
        reply = self.sendAndReply('SAVE E ' + str(scanNumber) + ' ' + str(startPos) + ' ' + str(stopPos) + ' ' + str(stepSize));
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] == 'SAVED':
            print 'Classix saves images successfully.'
            return True;
        else:
            print 'Porblem when Classix saving images: ' + reply;
            return True;
    

    def getImageIntegration(self):
        while self.checkStatus() != 'READY':
            sleep(1);
        
        reply = self.sendAndReply('IMAG');
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'IMAGD':
            print "Error: " + reply;
        else:
            rf=float(rlist[1]);
            return rf;

    def startImageCollection(self, newExpos):
        while self.checkStatus() != 'READY':
            sleep(1);
        reply = self.sendAndReply('IMAG ' + str(newExpos) );
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'OK':
            print "Server replied wrong message: " + reply;
        return;
    
    def checkStatus(self):
        reply = self.sendAndReply('STAT');
        print "Current status is: " + reply;
        rlist=reply.strip(' \n\r').split(' ',1);
        return rlist[0];


    #PseudoDetector Implementation
    def getPosition(self):
        return self.readout();
        
    def asynchronousMoveTo(self,newExpos):
        self.setCollectionTime(newExpos)
        self.collectData();

#    def moveTo(self, newPos):
#        self.asynchronousMoveTo(newPos);
#        while self.isBusy():
#            sleep(5);

#    def waitWhileBusy(self):
#        while self.isBusy():
#            sleep(5);
#        return;

    def getCollectionTime(self):
        return self.exposureTime;

    def setCollectionTime(self, newExpos):
        self.exposureTime = newExpos;

    def collectData(self):
        self.startImageCollection(self.exposureTime);
        return;
    
    def readout(self):
        return self.getImageIntegration();

    def getStatus(self):
        IDLE = 0;
        BUSY = 1;
        FAULT = 3;
        if self.checkStatus() =='READY':
            return IDLE;
        else:
            return BUSY;

    #Only used for oly ScannableBase, not the new PseudoDetector
#    def isBusy(self):
#        if  self.checkStatus() == 'READY':
#            return False;
#        else:
#            return Ture;

    def singleShot(self, newExpos):
        self.setCollectionTime(newExpos);
        self.collectData();
        self.readout();
        
    def getScanNumber(self):
        nt = NumTracker("tmp")
        #get current scan number
        return int(nt.getCurrentFileNumber());
        

print "Note: Use object name 'camera' for Classix camera";
camera = ClassixCameraDeviceClass('camera','diamrl5068.diamond.ac.uk', 2729 );
#camera = ClassixCameraDeviceClass('camera','172.23.106.152', 6342 );
