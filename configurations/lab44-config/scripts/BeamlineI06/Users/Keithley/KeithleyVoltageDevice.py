
from time import sleep
from gda.device.scannable import PseudoDevice
from gda.epics import CAClient 

import __main__ as gdamain

#Create Pseudo Device for Keithley2000 MultipleMetere controlled over Epics Patch Panel
class Keithley2000VoltageDeviceClass(PseudoDevice):
    def __init__(self, name, pvIn, pvOut):
        self.setName(name);
        self.setInputNames(['voltage']);
        self.setOutputFormat(["%10.6f"]);
        #self.setUnits(['V']);
        self.setLevel(7);
        self.chIn=CAClient(pvIn);
        self.chIn.configure();
        self.chOut=CAClient(pvOut);
        self.chOut.configure();

    def getVoltage(self):
        self.chOut.caput(':FETCH?');
        sleep(0.5);
        v=self.chIn.caget();
        return float(v);

    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": Keithley 2000 Voltage readback: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        return self.getVoltage();

    def asynchronousMoveTo(self,time):
        print "The Keithley 2000 is a read only multipal meter.";

    def isBusy(self):
        return False;


#Create Pseudo Device for Keithley2600A System Source Meter controlled over Epics Patch Panel
class Keithley2600AVoltageDeviceClass(PseudoDevice):
    def __init__(self, name, channel, pvIn, pvOut):
        self.setName(name);
        self.setInputNames(['voltage']);
        self.setOutputFormat(["%10.6f"]);
        #self.setUnits(['V']);
        self.setLevel(7);
        self.channel = channel;
        self.strCommandSet = ['smua.source.levelv','smub.source.levelv'] ;
        self.strCommandGet = ['print(smua.source.levelv)','print(smub.source.levelv)'] ;

        self.chIn=CAClient(pvIn);
        self.chIn.configure();
        self.chOut=CAClient(pvOut);
        self.chOut.configure();

    def send(self, strCom):
        print "Out command: ", strCom;
        self.chOut.caput(strCom);
        sleep(0.2);
        v=self.chIn.caget();
        print "In String", v;
        return;

    def turnon(self):
        self.send('smua.source.output=1');
        self.send('smub.source.output=1')        

    def getVoltage(self):
        self.chOut.caput(self.strCommandGet[self.channel]);
        sleep(0.2);
        v=self.chIn.caget();
        print "In String", v;
        return float(v);

    def setVoltage(self, v):
        strOut = self.strCommandSet[self.channel] + '=' + str(round(v,5));
        print "Out String: " + strOut;
        self.chOut.caput(strOut);
        return;

    #PseudoDevice Implementation
    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": Keithley 2600A Voltage readback: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        return self.getVoltage();

    def asynchronousMoveTo(self, newVoltage):
        self.setVoltage(newVoltage);
        print "The Keithley 2600A voltage has been set.";

    def isBusy(self):
        sleep(1);
        return False;


class CurrentDeviceClass(PseudoDevice):
    def __init__(self, name, viName):
        self.setName(name);
        self.setInputNames(['current']);
        self.setOutputFormat(["%15.10f"]);
        #self.setUnits(['A']);
        self.setLevel(7);
        self.vi = vars(gdamain)[viName];

	
    def getCurrent(self):
        v=self.vi.getVoltage()/100.0;
        return float(v);

    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": Current readback: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        return self.getCurrent();

    def asynchronousMoveTo(self,time):
        print "The Keithley 2000 is a read only multipal meter.";

    def isBusy(self):
        return False;


class GateDeviceClass(PseudoDevice):
    def __init__(self, name, iName, vtName):
        self.setName(name);
        self.setInputNames(['current']);
        self.setOutputFormat(["%10.6f"]);
        #self.setUnits(['A']);
        self.setLevel(7);
        self.i = vars(gdamain)[iName];
        self.vt = vars(gdamain)[vtName];

    def getGate(self):
        v=self.i.getCurrent()/self.vt.getVoltage();
        return float(v);

    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": Current readback: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        return self.getGate();

    def asynchronousMoveTo(self,time):
        print "The Keithley 2000 is a read only multipal meter.";

    def isBusy(self):
        return False;


exec("[dmm, va, vb, i0, g]=[None, None, None, None, None]");

pvPatchPanelSerialPort1_In = 'BL06I-EA-USER-01:ASYN1.TINP';
pvPatchPanelSerialPort1_Out  = 'BL06I-EA-USER-01:ASYN1.AOUT';
dmm=Keithley2000VoltageDeviceClass('dmm',pvPatchPanelSerialPort1_In,pvPatchPanelSerialPort1_Out);

pvPatchPanelSerialPort2_In = 'BL06I-EA-USER-01:ASYN3.TINP';
pvPatchPanelSerialPort2_Out  = 'BL06I-EA-USER-01:ASYN3.AOUT';
va=Keithley2600AVoltageDeviceClass('va', 0, pvPatchPanelSerialPort2_In,pvPatchPanelSerialPort2_Out);
vb=Keithley2600AVoltageDeviceClass('vb', 1, pvPatchPanelSerialPort2_In,pvPatchPanelSerialPort2_Out);

i0= CurrentDeviceClass('i0', 'dmm');
g = GateDeviceClass('g', 'i0','vb');

