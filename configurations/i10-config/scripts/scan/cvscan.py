'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from gdascripts.scan.scanListener import ScanListener
from org.slf4j import LoggerFactory
from gdascripts.scan import trajscans
from gdascripts.scannable.installStandardScannableMetadataCollection import meta
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
from gda.jython.commands.GeneralCommands import alias 
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from numbers import Number
from com.sun.org.apache.xpath.internal import Arg
from scannable.continuous.continuous_energy_scannables import binpointGrtPitch_g,\
    binpointMirPitch_g, binpointPgmEnergy_g

class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")

    def prepareForScan(self):
        self.logger.info("prepareForCVScan()")

    def update(self, scanObject):
        self.logger.info("update(%r)" % scanObject)


trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta]

trajectory_controller_helper = TrajectoryControllerHelper()

print "-"*100
print "Creating I10 GDA 'cvscan' commands: - dwell time must apply to all waveform scannables individually!"
cvscan=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 
alias('cvscan')

print "Creating I10 GDA 'cvscan2' commands: - ensure dwell time is applied all waveform scannables individually!"
def cvscan2(c_energy, start, stop, step, *args):
    ''' cvscan that applies dwell time to all instances of WaveformChannelScannable.
        This will make sure all the waveform channel scannable data are polled at the same rate.
    '''
    wfs=[]
    dwell=[]
    others=[]
    newargs=[c_energy, start, stop, step]
    for arg in args:
        if isinstance(arg, WaveformChannelScannable):
            wfs.append(args)
        elif isinstance(arg, Number):
            dwell.append()
        else:
            others.append()
    if not checkContentEqual(dwell):
        raise Exception("dwell time specified must be equal for all detectors!")
    for each in wfs:
        newargs.append(each)
        newargs.append(dwell)
    if c_energy.getName() == "egy_g":
        #set dwell time to embedded instances of WaveformChannelScannable
        if binpointGrtPitch_g not in wfs:
            newargs.append(binpointGrtPitch_g)
            newargs.append(dwell)
        if binpointMirPitch_g not in wfs:
            newargs.append(binpointMirPitch_g)
            newargs.append(dwell)
        if binpointPgmEnergy_g not in wfs:
            newargs.append(binpointPgmEnergy_g)
            newargs.append(dwell)
    for other in others:
        newargs.append(other)
    cvscan([e for e in newargs])
    
def checkContentEqual(lst):
    return lst[1:] == lst[:-1]

alias("cvscan2")

# E.g. cvscan egy 695 705 1 mcs1 2 mcs17 2 mcs16 2

""" Tests Results:
    10ev at 2 seconds per 1ev 'step & 10ev at .2 seconds per .1ev 'step:

    scan pgm_energy 695 705 1 macr1 macr16 macr17 2       11 points, 28 seconds (18:32:36 to 18:33:24)
    scan pgm_energy 695 705 .1 macr1 macr16 macr17 .2    101 points, 3 minutes 15 seconds (18:35:57 to 18:39:12
    
    cvscan egy 695 705 1 mcs1 mcs16 mcs17 2                11 points, 34 seconds (18:41:48 to 18:42:22)
    cvscan egy 695 705 .1 mcs1 mcs16 mcs17 .2            101? points, 36 seconds (18:45:09 to 18:45:45)
"""