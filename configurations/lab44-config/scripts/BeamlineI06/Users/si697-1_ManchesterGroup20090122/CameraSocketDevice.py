from time import sleep
from java import lang

from gda.factory import Finder
from gda.data import NumTracker

#New style Pseudo devices use gda.device.scannable.ScannableMotionBase
#from gda.device.scannable import ScannableMotionBase
#New style Pseudo detectors use gda.device.detector.DetectorBase
#from gda.device.detector import DetectorBase

#Old style Pseudo devices use gda.device.scannable.ScannableBase
from gda.device.scannable import ScannableBase
from gda.device import Scannable

import socket

#The Class for creating a socket-based Psuedo Device
class CameraSockteDeviceClass(ScannableBase):
#class CameraSockteDeviceClass(DetectorBase):
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        self.setInputNames([]);
        self.setExtraNames([name]);
#        self.Units=[strUnit];
        self.setLevel(7);
        finder = Finder.getInstance();
        self.serverHost = hostName;
        self.serverPort = hostPort;
        self.exposureTime = 1;

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
#        self.socket.connect((self.serverHost,self.serverPort));
#        self.socket.send(returnChar) #send an empty return to clear any commands that aren't finished
#        self.socket.recv(1024) #clear the output buffer... should send back less than 20 characters

    #SocketDevice implementation        
    def setupServer(self, hostName, hostPort):
        self.serverHost = hostName;
        self.serverPort = hostPort;
    
    def sendAndReply(self, strSend):
        self.socket.connect((self.serverHost,self.serverPort));
        print 'Send out ->' + strSend;
        self.socket.send(strSend);
        data = self.socket.recv(1024);
        if not data:
            print "Host connection closed.";
            self.socket.close();
            return 0;
        
        print 'Received ->' + data; print;
        self.socket.close();
        return data;

    def send(self, strSend):
        self.socket.connect((self.serverHost,self.serverPort));
        print 'Send out ->' + strSend;
        self.socket.send(strSend);
        self.socket.close();
    
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


    #DetectorBase Implementation
    def getPosition(self):
        return self.readout();
        
    def asynchronousMoveTo(self,newExpos):
        self.setCollectionTime(newExpos)
        self.collectData();

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

    def isBusy(self):
        if  self.checkStatus() == 'READY':
            return False;
        else:
            return True;

    def singleShot(self, newExpos):
        self.setCollectionTime(newExpos);
        self.collectData();
        self.readout();
        
    def getScanNumber(self):
        nt = NumTracker("tmp")
        #get current scan number
        return int(nt.getCurrentFileNumber());
        
print "Note: Use object name 'camera' for Classix camera";
camera = CameraSockteDeviceClass('camera','172.23.106.152', 6342 );
