
from Diamond.Trough.IsothermScan import IsothermScanControlClass
                                        
from Diamond.Trough.TroughEpicsBridge import NimaLangmuirBlodgettTroughBridgeClass;
from Diamond.Trough.TroughDevices import TroughAreaDevice, TroughSpeedDevice, TroughPressureDevice

#Trough over EPICS-labVIEW bridge
rootPV='BL07I-TROUGH';
trough = NimaLangmuirBlodgettTroughBridgeClass('trough', rootPV);
#Trough over GDA RS232
#trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port2);


troughArea = TroughAreaDevice("troughArea", trough);
troughSpeed = TroughSpeedDevice("troughSpeed", trough);
troughPressure = TroughPressureDevice("troughPressure", trough);


trough.setSpeedLimits(3.5, 110);
trough.setSpeed(60);
trough.setAreaLimits(10, 500);

troughArea.reset();
troughPressure.reset();


#import Diamond.Trough.TroughEpicsDevice
#reload(Diamond.Trough.TroughEpicsDevice
#run "BeamlineI07/useTrough"
