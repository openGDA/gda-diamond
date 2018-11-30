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
from scannable.continuous.continuous_energy_scannables import binpointGrtPitch_g,\
    binpointMirPitch_g, binpointPgmEnergy_g, cemc_g, cemc
from scannable.checkbeanscannables import ZiePassthroughScannableDecorator
from scannable.idcontrols.mode_polarisation_energy_instances import smode, pol
from scannable.idcontrols.sourceModes import SourceMode
from scannable.idcontrols.polarisation import Polarisation
from scannable.id_energys.idd_energy_gap import idd_circ_pos_energy_follower,\
    idd_circ_neg_energy_follower, idd_lin_hor_energy_follower,\
    idd_lin_ver_energy_follower
from scannable.id_energys.idd_lin_energy import idd_lin_arbitrary_energy_follower
from scannable.id_energys.idu_energy_gap import idu_lin_hor3_energy_follower,\
    idu_circ_pos_energy_follower, idu_circ_neg_energy_follower,\
    idu_lin_hor_energy_follower, idu_lin_ver_energy_follower
from scannable.id_energys.idu_lin_energy import idu_lin_arbitrary_energy_follower

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
cvscan_traj=trajscans.CvScan([scan_processor, trajectory_controller_helper]) 


def getEnergyFollower4CurrentSmodePolarisation():
    id_energy_follower=None
    mode = smode.getPosition()
    polarisation = pol.getPosition()
    if mode == SourceMode.SOURCE_MODES[0]:
        if polarisation == Polarisation.POLARISATIONS[0]:
            id_energy_follower = idd_circ_pos_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[1]:
            id_energy_follower = idd_circ_neg_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[2]:
            id_energy_follower = idd_lin_hor_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[3]:
            id_energy_follower = idd_lin_ver_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[4]:
            id_energy_follower = idd_lin_arbitrary_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[5]:
            raise Exception('Polarisation %s for source mode % is not supported: Energy Calibration is not available!' % (polarisation, mode))
    elif mode == SourceMode.SOURCE_MODES[1]:
        if polarisation == Polarisation.POLARISATIONS[0]:
            id_energy_follower = idu_circ_pos_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[1]:
            id_energy_follower = idu_circ_neg_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[2]:
            id_energy_follower = idu_lin_hor_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[3]:
            id_energy_follower = idu_lin_ver_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[4]:
            id_energy_follower = idu_lin_arbitrary_energy_follower
        elif polarisation == Polarisation.POLARISATIONS[5]:
            id_energy_follower = idu_lin_hor3_energy_follower
    return id_energy_follower

def cvscan(c_energy, start, stop, step, *args):
    ''' cvscan that checks if there is enough time to collect data before topup when 'checkbeamcv' is used,
    it also supports dynamically motion controller switch for energy object 'egy_g' or 'egy' depending on source mode and polarisation
    and append correct ID energy follower for  'egy_g' or 'egy'.    
    '''
    wfs=[]
    dwell=[]
    others=[]
    beam_checker=None
    newargs=[c_energy, start, stop, step]
    try:
        for arg in args:
            if isinstance(arg, WaveformChannelScannable):
                wfs.append(arg)
            elif isinstance(arg, Number):
                dwell.append(arg)
            elif isinstance(arg, ZiePassthroughScannableDecorator):
                beam_checker=arg
            else:
                others.append(arg)
        if not checkContentEqual(dwell):
            raise Exception("dwell time specified must be equal for all detectors!")
        for each in wfs:
            newargs.append(each)
            newargs.append(dwell[0])
        if c_energy.getName() == "egy_g":
            for each in wfs:
                each.setHardwareTriggerProvider(cemc_g) # switch to ContinuousPgmGratingEnergyMoveController
            id_energy_follower = getEnergyFollower4CurrentSmodePolarisation()
            if id_energy_follower is not None:
                newargs.append(id_energy_follower) # add the ID energy follower     
        elif c_energy.getName() == "egy":
            for each in wfs:
                each.setHardwareTriggerProvider(cemc) #switch to ContinuousPgmEnergyMoveController
            id_energy_follower = getEnergyFollower4CurrentSmodePolarisation()
            if id_energy_follower is not None:
                newargs.append(id_energy_follower) # add the ID energy follower     
        for other in others:
            newargs.append(other)
        if beam_checker is not None:
            #check if there is enough time for the cvscan before topup
            scanTime=abs((stop-start)/step*dwell[0]+5) # add extra 5 second to wait topup time.
            topup_checker=beam_checker.getDelegate().getGroupMember("checktopup_time_cv")
            topup_checker.minimumThreshold=scanTime
    #         print "topup_checker.minimumThreshold = %r" % (topup_checker.minimumThreshold)
            newargs.append(beam_checker)
        cvscan_traj([e for e in newargs])
    finally:
        if c_energy.getName() == "egy_g" or c_energy.getName() == "egy":
            for each in wfs:
                each.setHardwareTriggerProvider(energycontroller)  # @UndefinedVariable
        

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
    try:
        for arg in args:
            if isinstance(arg, WaveformChannelScannable):
                wfs.append(arg)
            elif isinstance(arg, Number):
                dwell.append(arg)
            elif isinstance(arg, ZiePassthroughScannableDecorator):
                beam_checker=arg
            else:
                others.append(arg)
        if not checkContentEqual(dwell):
            raise Exception("dwell time specified must be equal for all detectors!")
        for each in wfs:
            newargs.append(each)
            newargs.append(dwell)
        if c_energy.getName() == "egy_g":
            for each in wfs:
                each.setHardwareTriggerProvider(cemc_g) # switch to ContinuousPgmGratingEnergyMoveController
            id_energy_follower = getEnergyFollower4CurrentSmodePolarisation()
            if id_energy_follower is not None:
                newargs.append(id_energy_follower) # add the ID energy follower     
        elif c_energy.getName() == "egy":
            for each in wfs:
                each.setHardwareTriggerProvider(cemc) #switch to ContinuousPgmEnergyMoveController
            id_energy_follower = getEnergyFollower4CurrentSmodePolarisation()
            if id_energy_follower is not None:
                newargs.append(id_energy_follower) # add the ID energy follower     
        if c_energy.getName() == "egy_g" or c_energy.getName() == "egy":
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
        if beam_checker is not None:
            #check if there is enough time for the cvscan before topup
            scanTime=abs((stop-start)/step*dwell[0])
            topup_checker=beam_checker.getDelegate().getGroupMember("checktopup_time_cv")
            topup_checker.minimumThreshold=scanTime+5
            newargs.append(beam_checker)
        cvscan_traj([e for e in newargs])
    finally:
        if c_energy.getName() == "egy_g" or c_energy.getName() == "egy":
            for each in wfs:
                each.setHardwareTriggerProvider(energycontroller)  # @UndefinedVariable
    
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