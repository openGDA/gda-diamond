from time import sleep
from java import lang

from gda.factory import Finder

#New style Pseudo devices use gda.device.scannable.ScannableMotionBase
#from gda.device.scannable import ScannableMotionBase

#Old style Pseudo devices use gda.device.scannable.ScannableBase
from gda.device import Scannable
from gda.device.scannable import ScannableBase

import socket

#The Class for creating a socket-based Psuedo Device
class FilterSockteDeviceClass(ScannableBase):
#class FilterSockteDeviceClass(ScannableMotionBase):
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        self.setInputNames([]);
        self.setExtraNames([name]);
#        self.Units=[strUnit];
        self.setLevel(7);
        finder = Finder.getInstance();
        self.serverHost = hostName;
        self.serverPort = hostPort;

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        
    def setupServer(self, hostName, hostPort):
        self.serverHost = hostName;
        self.serverPort = hostPort;

    #SocketDevice implementation        
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
        reply = self.sendAndReply('SAVE F ' + str(scanNumber) + ' ' + str(startPos) + ' ' + str(stopPos) + ' ' + str(stepSize));
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] == 'SAVED':
            print 'Classix saves images successfully.'
            return True;
        else:
            print 'Porblem when Classix saving images: ' + reply;
            return True;


    def getFilterPosition(self):
        reply = self.sendAndReply('FILT');
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'FILTD':
            print "Error: " + reply;
            rf = 999;
        else:
            rf=int(float(rlist[1]));
            return rf;
        
    def checkStatus(self):
        reply = self.sendAndReply('STAT');
        print "Current status is: " + reply;
        rlist=reply.strip(' \n\r').split(' ',1);
        return rlist[0];

    #ScannableMotionBase Implementation
    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": Current filter position is: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        while self.isBusy():
            sleep(5);
        return self.getFilterPosition();
    
    def asynchronousMoveTo(self,newPos):
        reply = self.sendAndReply('FILT ' + str(newPos) );
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'OK':
            print "Server replied wrong message: " + reply;
        
        return;

#    def moveTo(self, newPos):
#        self.asynchronousMoveTo(newPos);
#        while self.isBusy():
#            sleep(5);

    def waitWhileBusy(self):
        while self.isBusy():
            sleep(5);
        return;

    def isBusy(self):
        if  self.checkStatus() == 'READY':
            return False;
        else:
            return True;

    def getScanNumber(self):
        nt = NumTracker("tmp")
        #get current scan number
        return int(nt.getCurrentFileNumber());

print "Note: Use object name 'filter' for Classix image filter";
filter = FilterSockteDeviceClass('filter','172.23.106.152', 6342 );
