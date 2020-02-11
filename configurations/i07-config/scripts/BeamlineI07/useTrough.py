#import Diamond.Trough.TroughWebServiceBridge
#reload(Diamond.Trough.TroughWebServiceBridge)

#import Diamond.Trough.TroughDevices
#reload(Diamond.Trough.TroughDevices)

from Diamond.Trough.TroughWebServiceBridge import NimaLangmuirBlodgettTroughBridgeClass;
from Diamond.Trough.TroughDevices import TroughAreaDevice, TroughSpeedDevice, TroughPressureDevice
from Diamond.Trough.IsothermScan import IsothermScanControlClass

#Trough using WebService over LabVIEW
#Example url for reading all: 'http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_ReadAll/localhost''

#wsHost='diamrd2316.diamond.ac.uk'
wsHost='diamrl5344.diamond.ac.uk'

#dsHost='diamrd2316.diamond.ac.uk'
dsHost='diamrl5344.diamond.ac.uk'

trough = NimaLangmuirBlodgettTroughBridgeClass('trough', wsHost, dsHost);
#trough.setHosts(webServiceHostName='i07-solo.diamond.ac.uk', dataSocketHostName='diamrd2316.diamond.ac.uk')

troughArea = TroughAreaDevice("troughArea", trough);
troughArea.setDeadband(5);
troughArea.setMolecularProperties(312, 1.004, 10.0 );

troughPressure = TroughPressureDevice("troughPressure", trough);
troughPressure.setDeadband(1)

troughSpeed = TroughSpeedDevice("troughSpeed", troughArea);


trough.sync();
trough.setSpeedLimits(3.5, 250);
trough.setSpeed(200);
trough.setAreaLimits(50, 1000);
trough.setSpeedCorrectionFactor(2.0);


print "Trough control in GDA: "
print "    Device troughArea is used to change/scan the trough area"
print "    Device troughPressure is used to change/scan the pressure"
print "    Device troughSpeed is used to change the trough barrier speed"
print " "


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
print "To do the isotherm scan:"
print "    isoscan 100 220 60 2"
print "The above scan will change the area from 100 to 220 in 60 seconds, and record data on every 2 seconds"
print "which will set a speed of : 2 cm2/second, or 120 cm2/minute, and in total 30 data points collected"
#isoscan 100 220 60 2
