#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP


import time
from gda.device.scannable import ScannableBase
import socket


#The Class for creating a socket-based Psuedo Device to control the magnet
class vmagScannable(ScannableBase):
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        #self.setInputNames(['field']);
        #self.setOutputFormat(["%10.4f"]);
        self.input_Names = ['field', 'theta', 'phi']
        self.output_Formats= ["%10.4f", "%10.2f", "%10.2f"]
        self.setInputNames(self.input_Names);
        self.setOutputFormat(self.output_Formats);
        #self.setExtraNames(['field']);
        #self.Units=['mT'];
        self.setLevel(7);
        self.serverHost = hostName;
        self.serverPort = hostPort;
        
        self.SINGLEINPUT=False
        
        self.field=0;
        self.theta=0;
        self.phi=0;
        
        self.anglesFlipped=0
        
        self.iambusy = 0 
        


   
    def sendAndReply(self, strSend):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.socket.connect((self.serverHost, self.serverPort));
        self.socket.send(strSend);
        data = self.socket.recv(1024);       
        self.socket.close();
        return data;

    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;



    def setAngle(self, theta, phi):
        self.theta = theta
        self.phi = phi
        self.setRawAngle(theta,phi)
        self.anglesFlipped=0
    
    
    def setRawAngle(self, theta, phi):
        self.iambusy = 1
        cmd='setFieldDirection %(v1)10.2f %(v2)10.2f\n\r' %{'v1': theta, 'v2': phi};
        reply = self.sendAndReply(cmd);
        time.sleep(0.5);   
        self.iambusy = 0 
        
        
    def setField(self,field):
        self.iambusy = 1
        
        if field < 0:
            if (self.anglesFlipped == 0):
                self.setRawAngle(-self.theta, (self.phi+180)%360)
                self.anglesFlipped = 1
                print "flipping angles"
        else:
            if (self.anglesFlipped == 1):
                self.setRawAngle(self.theta, self.phi)
                self.anglesFlipped = 0
                print "unflipping angles"

        
        #Always call setField <field> <timeout> as may have been zerod for safety reason
        cmd='setField %(v1)10.4f 600000000\n\r' %{'v1': abs(field)/1000.0};
        reply = self.sendAndReply(cmd);
        self.field = field
        time.sleep(0.5);
        self.iambusy =0
        
        
    def asynchronousMoveTo(self,newPos):
        if isinstance(newPos,(int, float)):
            self.setInputNames([self.input_Names[0]])
            self.setOutputFormat([self.output_Formats[0]])
            self.setField(newPos)
            self.SINGLEINPUT=True
        elif isinstance(newPos, (list, tuple)):
            self.setInputNames(self.input_Names)
            self.setOutputFormat(self.output_Formats)
            self.setAngle(newPos[1], newPos[2])
            self.setField(newPos[0])
            self.SINGLEINPUT=False
        else:
            raise ValueError("Argument must be single float or a list of 3 float value")
        
        
        
    def getPosition(self):
        if (self.SINGLEINPUT):
            return self.field
        else:
            return [self.field, self.theta, self.phi]
        
        
    def toString(self):
        if self.SINGLEINPUT:
            ss=self.getName() + " [field]: " + str(self.getPosition());
        else:
            ss=self.getName() + " [field, theta, phi]: " + str(self.getPosition());
        return ss;
        
    def isBusy(self):
        return self.iambusy  
    
    
    def degauss(self):
        for h in range(600, 0, -50):
            print h
            self.setField(h/1000.0)
            time.sleep(0.5)
            self.setField(0)
            self.setField(-h/1000.0)
            time.sleep(0.5)   
            self.setField(0)        

"""####################################+#######################################"""

class vmagThetaScannable(ScannableBase):
    def __init__(self, vmag):
            self.name = "vmagTheta"
            self.setInputNames(["vmagTheta"])
            self.setOutputFormat(["%03d"])
            self.iambusy = 0 
            self.vmag = vmag

    def getPosition(self):
        return self.vmag.theta

    def asynchronousMoveTo(self, value):
        self.iambusy = 1
        self.vmag.setAngle(value, self.vmag.phi)
        self.iambusy = 0

    def isBusy(self):
        return self.iambusy

"""####################################+#######################################"""


class vmagPhiScannable(ScannableBase):
    def __init__(self, vmag):
            self.name = "vmagPhi"
            self.setInputNames(["vmagPhi"])
            self.setOutputFormat(["%03d"])
            self.iambusy = 0 
            self.vmag = vmag

    def getPosition(self):
        return self.vmag.phi

    def asynchronousMoveTo(self, value):
        self.iambusy = 1
        self.vmag.setAngle(self.vmag.theta, value)
        self.iambusy = 0

    def isBusy(self):
        return self.iambusy
