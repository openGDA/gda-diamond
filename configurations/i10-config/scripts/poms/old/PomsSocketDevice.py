#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

# Taken from /dls/i06-1/scripts/POMS/PomsSocketDevice.py on 5-Jul-2012 (not
# under version control).

from time import sleep
from java import lang

from gda.device.scannable import ScannableBase

import socket
import random

import __main__ as gdamain  # @UnresolvedImport

#The Class for creating a socket-based Psuedo Device to control the magnet
class PomsSocketDeviceClass(ScannableBase):
    """ This sets the field in the POMS, using the array argument [field_Tesla, theta_Deg, phi_Deg]
    e.g.
        >>> pos vmag [0.1 0 180]
    """
    def __init__(self, name, hostName, hostPort):
        self.setName(name);
        self.input_names=['field', 'theta', 'phi']
        self.setInputNames(self.input_names);
        self.output_formats=["%10.4f", "%10.2f", "%10.2f"]
        self.setOutputFormat(self.output_formats);
        #self.setExtraNames(['field']);
        self.Units=['Tesla','Deg','Deg'];
        self.setLevel(7);
        self.serverHost = hostName;
        self.serverPort = hostPort;
        self.field=None;
        self.theta=None;
        self.phi=None;
        self.verbose=False
        self.alreadyBusy=False
        self.FIRSTTIME=False
        self.SCANNING=False
        self.SINGLEINPUT=False

        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);

    def __repr__(self):
        pomformat = "PomsSocketDeviceClass(name=%r, hostName=%r, hostPort=%r)"
        return pomformat % (self.name, self.serverHost, self.serverPort)

    def setupServer(self, hostName, hostPort):
        self.serverHost = hostName;
        self.serverPort = hostPort;

    def connect(self):
        self.socket.connect((self.serverHost, self.serverPort));

    def close(self):
        self.socket.close();

    #SocketDevice implementation        
    def sendAndReply(self, strSend):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.socket.connect((self.serverHost, self.serverPort));
        if self.verbose:
            print 'Send out ->' + strSend;
        self.socket.send(strSend);
        data = self.socket.recv(1024);
        if not data:
            print "Host connection closed.";
            self.socket.close();
            return 0;
        
        if self.verbose:
            print 'Received ->' + data; print;
        self.socket.close();
        return data;

    def send(self, strSend):
        self.socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.socket.connect((self.serverHost,self.serverPort));
        if self.verbose:
            print 'Send out ->' + strSend;
        self.socket.send(strSend);
        self.socket.close();

    def hello(self):
        print self.sendAndReply('Hello\n\r');

    def getPomPosition(self):
        reply = self.sendAndReply('FILT');
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] != 'FILTD':
            print "Error: " + reply;
            rf = 999;
        else:
            rf=int(float(rlist[1]));
            return rf;
        
    #ScannableMotionBase Implementation
    def atScanStart(self):
        self.FIRSTTIME=True
        self.SCANNING=True

    def atScanEnd(self):
        self.SCANNING=False
        return;
    
    def toString(self):
        if self.SINGLEINPUT:
            ss=self.getName() + " [field]: " + str(self.getPosition());
        else:
            ss=self.getName() + " [field, theta, phi]: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        if self.SINGLEINPUT:
            return self.field
        else:
            return [self.field, self.theta, self.phi];
    
    def asynchronousMoveTo(self,newPos):
        if self.verbose:
            print "asynchronousMoveTo(%r)" % newPos
        self.alreadyBusy=True
        if not self.SCANNING or self.FIRSTTIME:
            # always parse for 'pos', but only parse once at the start in scan
            #configure names field to support pretty print
            if isinstance(newPos,(int, float)):
                self.setInputNames([self.input_names[0]])
                self.setOutputFormat([self.output_formats[0]])
                self.SINGLEINPUT=True
            elif isinstance(newPos, (list, tuple)):
                self.setInputNames(self.input_names)
                self.setOutputFormat(self.output_formats)
                self.SINGLEINPUT=False
            else:
                raise ValueError("Argument must be single float or a list of 3 float value")
            self.FIRSTTIME=False
            
        if not self.SINGLEINPUT:
            #To check if theta and phi will be changed:
            if self.theta != newPos[1] or self.phi != newPos[2]:
                cmd='setFieldDirection %(v1)10.2f %(v2)10.2f\n\r' %{'v1': newPos[1], 'v2': newPos[2]};
                reply = self.sendAndReply(cmd);
                rlist=reply.strip(' \n\r').split(' ',1);
                if rlist[0] == 'ERROR:':
                    print "The moke3d command setFieldDirection failed with reply: " + reply;
                else:
                    if self.verbose:
                        print "Angle set correctly";
                    self.theta = newPos[1];
                    self.phi = newPos[2];
            else:
                if self.verbose:
                    print 'No change of angle';
            sleep(0.5);

        #Always call setField <field> <timeout> as may have been zerod for safety reason
        if self.SINGLEINPUT:
            cmd='setField %(v1)10.4f 600000000\n\r' %{'v1': float(newPos)};
        else:
            cmd='setField %(v1)10.4f 600000000\n\r' %{'v1': newPos[0]};
        reply = self.sendAndReply(cmd);
        rlist=reply.strip(' \n\r').split(' ',1);
        if rlist[0] == 'ERROR:':
            print "The moke3d command setField FAILED with reply" + reply;
        else:
            if self.verbose:
                print "Field set correctly";
            if self.SINGLEINPUT:
                self.field=float(newPos)
            else:
                self.field = newPos[0];

        sleep(0.5);
        self.alreadyBusy=False
        return;

    def isBusy(self):
        #sleep(1);
        return self.alreadyBusy

