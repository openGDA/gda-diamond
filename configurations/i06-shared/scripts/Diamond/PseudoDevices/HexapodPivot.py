
from time import sleep;

from Diamond.Objects.EpicsPv import EpicsButtonClass
from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass



class HexapodPivotDeviceClass(EpicsDeviceClass):
    
    def __init__(self, name, pvName, syncButton, homeButton):
        
        strUnit='mm';
        strFormat='%8.5f';
        pvGet = pvName
        pvSet = pvName
        pvStatus=None;
        timeout=None;
        EpicsDeviceClass.__init__(self, name, pvSet, pvGet, pvStatus, strUnit, strFormat, timeout);
        self.syncButton=syncButton;
        self.homeButton=homeButton;
        

    def asynchronousMoveTo(self, new_position):
#        EpicsDeviceClass.asynchronousMoveTo(self, new_position);
        super(HexapodPivotDeviceClass, self).asynchronousMoveTo(new_position);
        
        self.syncButton.press();
        
    def sync(self):
        self.syncButton.press();
        sleep(2)
        
    def reset(self):
        self.homeButton.press();
        sleep(2)


#example:
#deviceNamePivotX="HEX1.PIVOTX";

#synchronizeDemaondButtonPV='BL07I-MO-HEX-01:SYNCDEMANDS.PROC';
#HomeAndCalibrateButtonPV='BL07I-MO-HEX-01:INIT.PROC';

#syncButton = EpicsButtonClass(synchronizeDemaondButtonPV);
#homeButton = EpicsButtonClass(HomeAndCalibrateButtonPV);

#hex1pivotx=HexapodPivotDeviceClass('hex1pivotx', deviceNamePivotX, syncButton, homeButton)
