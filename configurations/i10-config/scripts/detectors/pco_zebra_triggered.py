'''
Created on 5 Apr 2018

@author: fy65
'''
from future.scannable.ZebraTriggeredDetector import ZebraTriggeredDetector
from gdaserver import zebra

print "-"*100
print "Create Zebra triggered PCO detector - 'pcoz'"

in4ttl=10
setCollectionTimeInstructions = "Setting collection time in Zebra"
prepareForCollectionInstructions=None
scanStartInstructions="""
If you are having problems, or you are stuck only able to see this text:
    On the CamWare screen, make sure that:
        In Camera Control, teh Trigger mode is set to External Exp. Ctrl
    Then File menu > Direct Record To File,
        Set number of images to store as number of points in scan +1 or greater
        Set the name of the file for this scan.
On the Zebra EDM screen (Launchers > Beamlines > BL10I BLADE > ZEB1) ensure that:
    On the SYS tab:
        OUT4 TTL is 55 (PULSE4)
    On the PULSE tab, ensure that:
        PULSE4 input is 63 (SOFT_IN4) and Trigger on Rising Edge
Also make sure that:
    The Zebra TTL Out 4 is connected to the Camera exp. trig (control in)
    The Zebra TTL In 4  is connected to the Camera busy (status out)
    Ensure that the dip switches beneath the control in sockets are all set to ON"""
pcoz = ZebraTriggeredDetector('pcoz', zebra=zebra, 
    notScanInput=in4ttl, notReadyInput=None, triggerOutSoftInput=4,
    setCollectionTimeInstructions=setCollectionTimeInstructions,
    prepareForCollectionInstructions=prepareForCollectionInstructions,
    scanStartInstructions=scanStartInstructions, 
    gateNotTrigger=True, notScanInverted=True, zebraPulse=4)
