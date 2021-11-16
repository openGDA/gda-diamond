'''
    An extended GDA command to invoke the I06 constant velocity scan on energy by using the 
    FastEnergyDeviceClass.cvscan(startEnergy, endEnergy, scanTime, pointTime) method
    Syntax:
            zacscan startEnergy endEnergy scanTime pointTime
        or:
            zacscan(startEnergy, endEnergy, scanTime, pointTime)
            
Created on 19 Apr 2017

@author: fy65
'''
from Diamond.PseudoDevices.FastEnergyScan import FastEnergyScanControlClass,\
    FastEnergyScanIDModeClass, EpicsWaveformDeviceClass, FastEnergyDeviceClass

import sys;

from gda.jython import InterfaceProvider;
from gda.jython.commands.GeneralCommands import alias

from Diamond.Utility.UtilFun import UtilFunctions
from Diamond.Utility.BeamlineFunctions import BeamlineFunctionClass, logger

from gda.configuration.properties import LocalProperties

uuu=UtilFunctions();
beamline_name = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME, "i06")
beamlineutil=BeamlineFunctionClass(beamline_name);
#exec('[fesController, zacmode, fesData, fastEnergy] = [None, None, None, None]')

if beamline_name=="i06-1":
    rootPV = "BL06J-MO-FSCAN-02"
elif beamline_name=="i06":
    rootPV = "BL06I-MO-FSCAN-02"
else:
    raise ValueError("'rootPV' is NOT specified!")

fastScanElementCounter="iduFastScanElementCounter"

fesController = FastEnergyScanControlClass("fesController", rootPV);
zacmode = FastEnergyScanIDModeClass("zacmode", fesController);
#fesData = EpicsScandataDeviceClass("fesData", rootPV);
fesData = EpicsWaveformDeviceClass("fesData", rootPV, ['C1','C2', 'C3', 'C4', 'iduenergy', 'pgmenergy', 'C5', 'C6'], ['idio', 'ifio', 'ifioft', 'ifiofb'],elementCounter=fastScanElementCounter);
fastEnergy = FastEnergyDeviceClass("fastEnergy", fesController, fesData);
fastEnergy.filterByEnergy = False
ROI_DEFINED_IN_GUI=True

if beamline_name == "i06":
    #configure KB Mirror rastering
    HYTEC_KB_Rastering_Control_PV="BL06I-OP-KBM-01:VFM:FPITCH:FREQ"
    KEYSIGHT_KB_Rastering_Control_PV="BL06I-EA-SGEN-01:PERIOD"
    fesController.setKBRasteringControlPV(HYTEC_KB_Rastering_Control_PV)
    #fesController.setKBRasteringControlPV(KEYSIGHT_KB_Rastering_Control_PV) 
    from __main__ import zacmedipix  # @UnresolvedImport
    ### configure which area detector to use in zacscan           
    ### use 'zacmedipixtif' for zacscan with Medipix to produce TIFF image files
    ### use 'zacmedipix' for zacscan with Medipix to produce Nexus and HDF files
    fesController.setAreaDetector(zacmedipix)

def zacscan(startEnergy, endEnergy, scanTime, pointTime):
    try:
        uuu.backupDefaults();
        if beamline_name=="i06-1":
            #TODO ask Sarnjeet for an update
            uuu.removeDefaults(['ca61sr', 'ca62sr','ca63sr','ca64sr','ca65sr','ca66sr']);

        if beamline_name=="i06" and not ROI_DEFINED_IN_GUI:
                #setup ROIs
                assert not roi1 or not roi2 or not roi3 or not roi4, "4 Region of Interests: 'roi1', 'roi2', 'roi3', and 'roi4' are required."  # @UndefinedVariable
                fesController.setupAreaDetectorROIs([roi1, roi2, roi3, roi4])  # @UndefinedVariable
        beamlineutil.stopArchiving();
        fastEnergy.cvscan(startEnergy, endEnergy, scanTime, pointTime);
        beamlineutil.registerFileForArchiving( beamlineutil.getLastScanFile() );
        beamlineutil.restoreArchiving();

        uuu.restoreDefaults();
        
    except :
        errortype, exception, traceback = sys.exc_info();
        logger.fullLog(None, "Error in zacscan", errortype, exception , traceback, False);        

alias("zacscan");

def zacstop():
    try:
        fastEnergy.stop();
        beamlineutil.restoreArchiving();
        InterfaceProvider.getCommandAborter().abortCommands()
    except :
        errortype, exception, traceback = sys.exc_info();
        logger.fullLog(None, "Error in stopping the zacscan ", errortype, exception , traceback, False);        


##        if (this.commandserver.getScanStatus() == Jython.RUNNING || this.commandserver.getScanStatus() == Jython.PAUSED) {
##            this.commandserver.haltCurrentScan();
##        } else {
##            this.commandserver.haltCurrentScript();
##        }
##    commandserver.panicStop();

alias("zacstop");

from gda.jython.commands.ScannableCommands import pscan

"""
    An External function to run the I06 energy constant velocity scan by using the  FastEnergyScanClass class
    This method is for debug only and should be replaced by the above zacscan command 
"""
def fastscan(startEnergy, endEnergy, scanTime, pointTime):
    fesData.reset();
    fesController.setEnergyRange(startEnergy, endEnergy);
    fesController.setTime(scanTime, pointTime);
    fesController.setIDMode(1);

    if pointTime > 2.0:
        fastEnergy.setDelay(pointTime/2.0);
    elif pointTime>0.5:
        fastEnergy.setDelay(pointTime/5.0);
    else:
        fastEnergy.setDelay(pointTime/10.0);
        
    
    numPoint = fesController.getNumberOfPoint();
    step=1.0*(endEnergy - startEnergy)/numPoint;
    
#    scan timer 0 scanTime pointTime fastEnergy 1 sdd 10
#    pscan fastEnergy 0 1 numPoint fesData 0 1;
    pscan([fastEnergy,0,1,numPoint,fesData,0,1]);


