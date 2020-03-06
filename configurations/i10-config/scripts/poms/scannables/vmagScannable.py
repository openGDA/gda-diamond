#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP


import time
from gda.device.scannable import ScannableBase
import socket

#The Class for creating a socket-based Psuedo Device to control the magnet
class vmagScannable(ScannableBase):
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        self.setInputNames(['field', 'theta', 'phi']);
        self.setExtraNames([])
        self.setOutputFormat(["%3.2f", "%3d", "%3d"]);
        self.Units=['mT', 'degrees', 'degrees'];
        self.setLevel(7);
        self.serverHost = hostName;
        self.serverPort = hostPort;
        
        self.field=0;
        self.theta=0;
        self.phi=0;
        self.anglesFlipped=0
        
        self.iambusy = 0 


    def sendAndReply(self, strSend):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.serverHost, self.serverPort))
        self.socket.send(strSend)
        data = self.socket.recv(1024)
        self.socket.close()
        return data;

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def setAngle(self, theta, phi):
        self.theta = theta
        self.phi = phi
        self.setRawAngle(theta,phi)
        self.anglesFlipped=0
    
    
    def setRawAngle(self, theta, phi):
        self.iambusy = 1
        cmd='setFieldDirection %(v1)10.2f %(v2)10.2f\n\r' %{'v1': theta, 'v2': phi};
        reply = self.sendAndReply(cmd);
        if (reply != "OK"): 
            self.iambusy = 0
            raise ValueError(reply)
        time.sleep(0.5)
        self.iambusy = 0
        
        
    def setField(self,field):
        self.iambusy = 1
        
        if field < 0:
            if (self.anglesFlipped == 0):
                self.setRawAngle(-self.theta, (self.phi+180)%360)
                self.anglesFlipped = 1
                #print "flipping angles"
        else:
            if (self.anglesFlipped == 1):
                self.setRawAngle(self.theta, self.phi)
                self.anglesFlipped = 0
                #print "unflipping angles"

        
        #Always call setField <field> <timeout> as may have been zerod for safety reason
        cmd='setField %(v1)10.6f 600000000\n\r' %{'v1': abs(field)/1000.0}
        reply = self.sendAndReply(cmd)
        if (reply != "OK"):
            self.iambusy =0
            raise ValueError(reply)
        self.field = field
        time.sleep(0.5)
        self.iambusy = 0
        
        
    def asynchronousMoveTo(self,newPos):
        if isinstance(newPos,(int, float)):
            self.setInputNames(['field'])
            self.setExtraNames(['theta', 'phi'])
            self.setField(newPos)
        elif isinstance(newPos, (list, tuple)):
            self.setInputNames(['field', 'theta', 'phi'])
            self.setExtraNames([])
            self.setAngle(newPos[1], newPos[2])
            self.setField(newPos[0])
        else:
            print type(newPos)
            raise ValueError("Argument must be single float or a list of 3 float value")
        
        
        
    def getPosition(self):
        return [self.field, self.theta, self.phi]

    def isBusy(self):
        return self.iambusy  


