
from time import sleep;

from Diamond.Objects.EpicsPv import EpicsButtonClass
from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
from Diamond.PseudoDevices.HexapodPivot import HexapodPivotDeviceClass;


deviceNamePivotX="HEX2.PIVOTX";
deviceNamePivotY="HEX2.PIVOTY";
deviceNamePivotZ="HEX2.PIVOTZ";

synchronizeDemaondButtonPV='BL07I-MO-HEX-01:SYNCDEMANDS.PROC';
HomeAndCalibrateButtonPV='BL07I-MO-HEX-01:INIT.PROC';

syncButton = EpicsButtonClass(synchronizeDemaondButtonPV);
homeButton = EpicsButtonClass(HomeAndCalibrateButtonPV);

hex2pivotx=HexapodPivotDeviceClass('hex2pivotx', deviceNamePivotX, syncButton, homeButton)
hex2pivoty=HexapodPivotDeviceClass('hex2pivoty', deviceNamePivotY, syncButton, homeButton)
hex2pivotz=HexapodPivotDeviceClass('hex2pivotz', deviceNamePivotZ, syncButton, homeButton)

HEX2.addGroupMember(hex2pivotx);
HEX2.addGroupMember(hex2pivoty);
HEX2.addGroupMember(hex2pivotz);

def hex2pivot():
    xpos = hex2x.getPosition()
    ypos = hex2y.getPosition()
    zpos = hex2z.getPosition()
    
    print "Pivot points set..."
#    hex2pivotx.moveTo( -1.0*xpos )
#    hex2pivoty.moveTo( -1.0*ypos )
#    hex2pivotz.moveTo( 420-zpos )

    hex2pivotx.caput( -1.0*xpos )
    hex2pivoty.caput( -1.0*ypos )
    hex2pivotz.caput( 420.0-zpos )
    hex2pivotx.sync();

    hl=HEX2.getGroupMembers()
    for h in hl:
        print h.toFormattedString();
        #print h.getName() + ": "+ str( h.getPosition());


def hex2reset():
    
    print "Stop HEX2 motors..."
    hl=HEX2.getGroupMembers()
    for h in hl:
        print "    To stop " + h.getName();
        h.stop();
        
    sleep(10)

    print "Reset errors..."
    hex2pivotx.reset();
    
    print "Synchronise demands..."
    hex2pivotx.sync();

    print "hex2 reset complete";
    print HEX2.toFormattedString();

alias("hex2pivot");
alias("hex2reset");
