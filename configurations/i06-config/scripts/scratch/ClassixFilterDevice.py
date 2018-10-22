from time import sleep
from java import lang

from gda.factory import Finder

#New style Pseudo devices use gda.device.scannable.PseudoDevice 
from gda.device.scannable import PseudoDevice

#Old style Pseudo devices use gda.device.scannable.ScannableBase
#from gda.device.scannable import ScannableBase
#from gda.device import Scannable

from temp.SocketDevice import SockteDeviceClass;

#The Class for creating a socket-based Psuedo Device
#class FilterSockteDeviceClass(ScannableBase):
class ClassixFilterDeviceClass(SockteDeviceClass, PseudoDevice):
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

    #PseudoDevice Implementation
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
filter = ClassixFilterDeviceClass('filter','diamrl5068.diamond.ac.uk', 2729 );
#filter = ClassixFilterDeviceClass('filter','172.23.106.152', 6342 );
