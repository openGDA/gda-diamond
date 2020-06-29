
from Diamond.Comm.SerialDevices import EpicsAsynRS232DeviceClass, GdaRS232DeviceClass;
from Diamond.Trough.IsothermScan import IsothermScanControlClass
                                        
from Diamond.Trough.TroughDevice import NimaLangmuirBlodgettTroughDeviceClass;
from Diamond.Trough.TroughDevice import TroughAreaDevice, TroughSpeedDevice, TroughPressureDevice

try:
    del port1
    del port2
    del trough
    del troughArea
    del troughSpeed
    del troughPressure
except:
    pass


#GDA RS232 communication
#c=Finder.find("com1")
#sc=Finder.find("sc1")

#sc.setCommandTerminator('')
#sc.setReplyTerminator('\r')
#sc.configure()
#c.flush()

#port2=GdaRS232DeviceClass(sc)

#EPICS RS232 communication
rootPV = "BL07I-EA-USER-01:ASYN2"
portName='ty_50_2'
baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
dataBits=EpicsAsynRS232DeviceClass.DATABITS['8']
parity=EpicsAsynRS232DeviceClass.PARITY['None']
flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None']
timeout=2;

port1 = EpicsAsynRS232DeviceClass(rootPV);
port1.setPort(portName, baudRate, dataBits, parity, flowControl, timeout);
#port1.setOutputTerminator('\r');
#port1.setInputTerminator('\r')
port1.setInputTerminator('\r')
port1.flush()

#Trough over EPICS RS232
trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port1);
#Trough over GDA RS232
#trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port2);



troughArea = TroughAreaDevice("troughArea", trough);
troughSpeed = TroughSpeedDevice("troughSpeed", trough);
troughPressure = TroughPressureDevice("troughPressure", trough);


trough.setSpeedLimits(3.5, 110);
trough.setAreaLimits(18, 73);

#A function to run the isotherm scan on Trough
def isoscan(startPosition, stopPosition,scanTime, pointTime):
    isoController = IsothermScanControlClass("isoController", trough);
#    isoController.setIndexChannel(0);#0 for the area, 5 for the time
    
    try:
        return isoController.isoscan(startPosition, stopPosition,scanTime, pointTime);
    except :
        type, exception, traceback = sys.exc_info();
        logger.fullLog(None, "Error in isoscan", type, exception , traceback, False);        


alias("isoscan")

#Usage:
print "To do the isotherm scan, for example:"
print "    to change the area from 20 to 50 in 60 seconds, and record data on every 2 seconds"
print "    need a speed of : 0.5cm2/second, or 30cm2/minute, and in total 30 data points collected"
print "Usage:" 
print "    isoscan 20 50 60 2"
#isoscan 200 300 20 2
