from time import sleep
from java import lang

#New style Pseudo devices use gda.device.scannable.ScannableMotionBase
from gda.device.scannable import ScannableMotionBase

#Old style Pseudo devices use gda.device.scannable.ScannableBase
#from gda.device.scannable import ScannableBase
#from gda.device import Scannable

import socket

#The Class for creating a socket-based Psuedo Device
#class SockteDeviceClass(ScannableBase):
class SockteDeviceClass(ScannableMotionBase):
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        self.setInputNames([]);
        self.setExtraNames([name]);
#        self.Units=[strUnit];
        self.setLevel(7);
        self.serverHost = hostName;
        self.serverPort = hostPort;

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
#        self.socket.connect((self.serverHost,self.serverPort));
#        self.socket.send(returnChar) #send an empty return to clear any commands that aren't finished
#        self.socket.recv(1024) #clear the output buffer... should send back less than 20 characters
        
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

       

    def atScanStart(self):
        return;

    #Scannable Implementations
    def getPosition(self):
        reply = self.sendAndReply('IMAG');
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'IMAG':
            print "Error: " + reply;
        else:
            rf=float(rlist[1]);
            return rf;
        
    def asynchronousMoveTo(self,newPos):
        reply = self.sendAndReply('IMAG ' + str(newPos) );
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'OK':
            print "Server replied wrong message: " + reply;
        
        return;

    def moveTo(self, new_position):
        printed = False;
        while self.isBusy():
            if not printed:
                print "Target object is busy, waiting...";
                printed = True;
            sleep(0.2);
            
        print "Target object is ready. Now moving...";
        self.refObj.moveTo(self.x);

        
    def checkStatus(self):
        reply = self.sendAndReply('STAT');
        print "Current status is: " + reply;
        rlist=reply.strip(' \n\r').split(' ',1);
        return rlist[0];


    def isBusy(self):
        if  self.checkStatus() == 'READY':
            return False;
        else:
            return Ture;

    def atScanEnd(self):
        return;

    def singleShot(self, newExpos):
        self.uview.setCollectionTime(newExpos);
        print self.uview.shotSingleImage();
        
    def getCollectionTime(self):
        print self.uview.getCollectionTime();

    def setCollectionTime(self, newExpos):
        self.uview.setCollectionTime(newExpos);



print "Note: Use object name 'uv' for UView Image data access";
sc = SockteDeviceClass('sc','diamrl5068.diamond.ac.uk', 2729 );
