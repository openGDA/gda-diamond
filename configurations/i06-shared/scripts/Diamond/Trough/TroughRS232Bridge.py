
from time import sleep;
import math

from gda.epics import CAClient;
from gda.device.scannable import ScannableMotionBase;
from gda.device import DeviceBase

from Diamond.Comm.SerialDevices import EpicsAsynRS232DeviceClass, GdaRS232DeviceClass;

import __main__ as gdamain


#The Class for creating a RS232 port based device to control the Nima Langmuir-Blodgett Trough
class NimaLangmuirBlodgettTroughDeviceClass(object):
    NLBT_CONTROL_MODE = {"SPEED"   : 0,
                         "PRESSURE": 1,
                         "AREA"    : 2 };
    
    def __init__(self, name, port):
        self.name = name;
#        self.setInputNames(['field', 'theta', 'phi']);
#        self.setOutputFormat(["%10.4f", "%10.2f", "%10.2f"]);
#       self.setExtraNames(['field']);
#        self.Units=['Telsa','Deg','Deg'];
#        self.setLevel(7);
        self.port=port;
        self.mode = None;
        self.speed = None;
        self.pressure = None;
        self.area = None;
        self.area2 = None;
        self.temperature = None;
        self.time = None;

        self.statevalue=None;
        self.attarget=None;
        
        self.minArea=0;
        self.maxArea=900;
        self.minSpeed=5;
        self.maxSpeed=100;
        
        self.running=False;
        
    def isRunning(self):
        return self.running;
    
    def dealComError(self):
        self.port.flush();

    def setAreaLimits(self, low, high):
        self.minArea, self.maxArea = low, high;

    def getAreaLimits(self):
        return [self.minArea, self.maxArea];
    
    def setSpeedLimits(self, low, high):
        self.minSpeed, self.maxSpeed = low, high;

    def getSpeedLimits(self):
        return [self.minSpeed, self.maxSpeed];
    
    def setMode(self, newMode):
        if newMode in self.NLBT_CONTROL_MODE.values():
            self.mode = self.NLBT_CONTROL_MODE.keys()[self.NLBT_CONTROL_MODE.values().index(newMode)]
        elif newMode.upper() in self.NLBT_CONTROL_MODE.keys():
            self.mode = newMode.upper();
        else:
            print "Please use the right mode: 'speed/pressure/area' or 0/1/2. ";
            return;
        
        command="MODE "+str(self.NLBT_CONTROL_MODE[self.mode]);
        try:
            reply=self.port.writeAndRead(command);
            if reply != "OK":
                print "Reply Error!"
                self.dealComError();
        except:
            print "Communication Error!"
            self.dealComError();
        
#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);

    def setArea(self, newValue):
        command="AREA "+str(newValue);
        try:
            reply=self.port.writeAndRead(command);
            if reply != "OK":
                print "Reply Error!"
                self.dealComError();
        except:
            print "Communication Error!"
            self.dealComError();

#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);
        
    def setPressure(self, newValue):
        command="PRES "+str(newValue);
        try:
            reply=self.port.writeAndRead(command);
            if reply != "OK":
                print "Reply Error!"
                self.dealComError();
        except:
            print "Communication Error!"
            self.dealComError();

#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);
        
    def setSpeed(self, newValue):
        command="SPEED "+str(newValue);
        try:
            reply=self.port.writeAndRead(command);
            if reply != "OK":
                print "Reply Error!"
                self.dealComError();
        except:
            print "Communication Error!"
            self.dealComError();
        
#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);

    def readValues(self):
        command="READ";
        try:
            reply=self.port.writeAndRead(command);
            values=reply.split(',');
            self.speed=float(values[0])
            self.pressure=float(values[1])
            self.area=float(values[2])
            self.area2=float(values[3])
            self.temperature=float(values[4])
            self.time=float(values[5]);
        except:
            print "Trough Communication Error!"
            self.dealComError();

#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);
        return [self.area, self.pressure, self.speed, self.area2, self.temperature, self.time];

    def getSpeed(self):
        self.readValues();
        return self.speed;
    
    def getArea(self):
        self.readValues();
        return self.area;
    
    def getPressure(self):
        self.readValues();
        return self.pressure;

    
    def getStatus(self):
        command="STATUS";
        try:
            reply=self.port.writeAndRead(command);
            values=reply.split(',');
            self.statevalue=int(values[0])
            self.attarget=int(values[1])
        except:
            print "Trough Communication Error!"
            self.dealComError();
            return False;
#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);
        if self.statevalue ==1 & self.attarget == 1: #Under Remote control and at target 
            return True
        else:
            return False;
        
        
    def start(self):
        if self.running:
            return;
        
        command="START";
        try:
            reply=self.port.writeAndRead(command);
            if reply != "OK":
                print "Reply Error!"
                self.dealComError();
        except:
            print "Trough Communication Error!"
            self.dealComError();

        self.running = True;
        
#        print "---> " + command;
#        print "<---" + reply;
        sleep(1);
        
    def stop(self):
        command="STOP";
        try:
            reply=self.port.writeAndRead(command);
            if reply != "OK":
                print "Reply Error!"
                self.dealComError();
        except:
            print "Trough Communication Error!"
            self.dealComError();

        self.running = False;
        
#        print "---> " + command;
#        print "<---" + reply;

    def asynchronousAreaMoveTo(self,newArea):
        self.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['AREA']);
        self.setArea(newArea);
        if not self.isRunning():
            self.start();

    def synchronousAreaMoveTo(self,newArea):
        self.asynchronousAreaMoveTo(newArea);
        while self.getStatus() is not True:
                sleep(5);


class TroughAreaDevice(ScannableMotionBase):
    def __init__(self, name, trough):
        self.setName(name);
        self.setInputNames(["Area"]);
        self.setExtraNames(["Pressure", "Temperature"]);
        self.setOutputFormat(["%8.4f", "%8.4f", "%8.4f"]);
        self.setLevel(7);
        self.trough = trough;

    #ScannableMotionBase Implementation
    def getPosition(self):
        self.trough.readValues()
        return [self.trough.area, self.trough.pressure, self.trough.temperature];

    def asynchronousMoveTo(self,newPos):
        self.trough.asynchronousAreaMoveTo(newPos);

    def isBusy(self):
        sleep(1)
        return not self.trough.getStatus()

    def stop(self):
        pass;

    def reset(self):
        self.trough.stop();
        

class TroughPressureDevice(ScannableMotionBase):
    def __init__(self, name, trough):
        self.setName(name);
        self.setInputNames(["Pressure"]);
        self.setExtraNames([]);
        self.setOutputFormat(["%8.4f"]);
        self.setLevel(7);
        self.trough = trough;

    def getPosition(self):
        self.trough.readValues()
        return self.trough.pressure;

    def asynchronousMoveTo(self,newPos):
        self.trough.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['PRESSURE']);
        self.trough.setPressure(newPos);
        if not self.trough.isRunning():
            self.trough.start();

    def isBusy(self):
        sleep(1)
        return not self.trough.getStatus()
    


class TroughSpeedDevice(ScannableMotionBase):
    def __init__(self, name, trough):
        self.setName(name);
        self.setInputNames(["Speed"]);
        self.setExtraNames([]);
        self.setOutputFormat(["%8.4f"]);
        self.setLevel(7);
        self.trough = trough;
        
    def getPosition(self):
        self.trough.readValues()
        return self.trough.speed;

    def asynchronousMoveTo(self,newPos):
        self.trough.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['SPEED']);
        self.trough.setSpeed(newPos);
#        if not self.trough.isRunning():
#            self.trough.start();

    def isBusy(self):
        return False;
    
   
#GDA RS232 communication
#c=Finder.find("com1")
#sc=Finder.find("sc1")

#sc.setCommandTerminator('')
#sc.setReplyTerminator('\r')
#sc.configure()
#c.flush()

#port2=GdaRS232DeviceClass(sc)

#EPICS RS232 communication
#rootPV = "BL07I-EA-USER-01:ASYN2"
#portName='ty_50_2'
#baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
#dataBits=EpicsAsynRS232DeviceClass.DATABITS['8']
#parity=EpicsAsynRS232DeviceClass.PARITY['None']
#flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None']
#timeout=2;

#port1 = EpicsAsynRS232DeviceClass(rootPV);
#port1.setPort(portName, baudRate, dataBits, parity, flowControl, timeout);

##port1.setOutputTerminator('\r');
#port1.setInputTerminator('\r')
#port1.flush()

##Trough over EPICS RS232
#trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port1);
#Trough over GDA RS232
#trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port2);


#troughArea = TroughAreaDevice("troughArea", trough);
#troughSpeed = TroughSpeedDevice("troughSpeed", trough);
#troughPressure = TroughPressureDevice("troughPressure", trough);

#trough.setSpeedLimits(10, 500);
#trough.setAreaLimits(0, 500);

