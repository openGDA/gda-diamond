
from time import sleep;

from Diamond.Objects.EpicsPv import EpicsButtonClass
from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass
from Diamond.PseudoDevices.HexapodPivot import HexapodPivotDeviceClass;


pvNamePivotX = "BL07I-MO-HEX-01:PIVOT:X"
pvNamePivotY = "BL07I-MO-HEX-01:PIVOT:Y"
pvNamePivotZ = "BL07I-MO-HEX-01:PIVOT:Z"

synchronizeDemaondButtonPV='BL07I-MO-HEX-01:SYNCDEMANDS.PROC';
HomeAndCalibrateButtonPV='BL07I-MO-HEX-01:INIT.PROC';

syncButton = EpicsButtonClass(synchronizeDemaondButtonPV);
homeButton = EpicsButtonClass(HomeAndCalibrateButtonPV);

hex1pivotx=HexapodPivotDeviceClass('hex1pivotx', pvNamePivotX, syncButton, homeButton)
hex1pivoty=HexapodPivotDeviceClass('hex1pivoty', pvNamePivotY, syncButton, homeButton)
hex1pivotz=HexapodPivotDeviceClass('hex1pivotz', pvNamePivotZ, syncButton, homeButton)

HEX1.addGroupMember(hex1pivotx);
HEX1.addGroupMember(hex1pivoty);
HEX1.addGroupMember(hex1pivotz);

def hex1pivot():
    xpos = hex1x.getPosition()
    ypos = hex1y.getPosition()
    zpos = hex1z.getPosition()
    
    print "Pivot points set..."
#    hex1pivotx.moveTo( -1.0*xpos )
#    hex1pivoty.moveTo( -1.0*ypos )
#    hex1pivotz.moveTo( 420-zpos )

    hex1pivotx.caput( -1.0*xpos )
    hex1pivoty.caput( -1.0*ypos )
    hex1pivotz.caput( 420.0-zpos )
    hex1pivotx.sync();

    hl=HEX1.getGroupMembers()
    for h in hl:
        print h.toFormattedString();
        #print h.getName() + ": "+ str( h.getPosition());


def hex1reset():
    
    print "Stop HEX1 motors..."
    hl=HEX1.getGroupMembers()
    for h in hl:
        print "    To stop " + h.getName();
        h.stop();
        
    sleep(10)

    print "Reset errors..."
    hex1pivotx.reset();
    
    print "Synchronise demands..."
    hex1pivotx.sync();

    print "hex1 reset complete";
    print HEX1.toFormattedString();

alias("hex1pivot");
alias("hex1reset");
