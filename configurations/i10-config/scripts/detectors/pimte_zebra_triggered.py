'''
Created on 5 Apr 2018

@author: fy65
'''
from future.scannable.ZebraTriggeredDetector import ZebraTriggeredDetector
from gdaserver import zebra

print "-"*100
print "Create Zebra triggered PIMTE detector - 'pimtez'"

in4ttl=10
in3ttl=7
setCollectionTimeInstructions = """    In addition:
    On the Main tab, as well as setting the exposure time, make sure that:
        Number of images is set to 1
        CCD Readout is set to Full
        Accumulations is set to 1
    On the Data File tab make sure that:
        The Data file is set to a suitable name and that it
        will be written to your visit directory
    On the ADC tab make sure that:
        Rate is set to 1MHz
    On the Timing tab make sure that:
        Mode is set to External Sync
        The Continuous Cleans checkbox is checked
        Shutter Control is Normal
        Safe mode is selected
        Delay time is 0.5seconds
        Edge trigger is + edge
Also make sure that:
    The Zebra TTL Out 4 is connected to the ST-133 Ext Sync input
    The Zebra TTL In 4  is connected to the ST-133 NOT SCAN output
    The Zebra TTL In 3  is connected to the ST-133 NOT READY output"""
prepareForCollectionInstructions="Please ensure that all acquisition parameters are correct before pressing the Acquire button."
pimtez = ZebraTriggeredDetector('pimtez', zebra=zebra, 
    notScanInput=in4ttl, notReadyInput=in3ttl, triggerOutSoftInput=4, 
    setCollectionTimeInstructions=setCollectionTimeInstructions, 
    prepareForCollectionInstructions=prepareForCollectionInstructions)