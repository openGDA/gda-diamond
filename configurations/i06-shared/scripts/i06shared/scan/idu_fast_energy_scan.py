'''
    An extended GDA command to invoke the I06 constant velocity scan on energy by using the 
    FastEnergyDeviceClass.cvscan(startEnergy, endEnergy, scanTime, pointTime) method
    Syntax:
            zacscan startEnergy endEnergy scanTime pointTime
        or:
            zacscan(startEnergy, endEnergy, scanTime, pointTime)
            
Created on 19 Apr 2017
updated on 20 Dec 2021 for medipix support

@author: fy65
'''
from Diamond.PseudoDevices.FastEnergyScan import FastEnergyScanControlClass,\
    FastEnergyScanIDModeClass, EpicsWaveformDeviceClass, FastEnergyDeviceClass
import sys
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import alias
from Diamond.Utility.UtilFun import UtilFunctions
from Diamond.Utility.BeamlineFunctions import BeamlineFunctionClass, logger
from gda.configuration.properties import LocalProperties

ENABLE_KB_RASTERING = True

uuu=UtilFunctions()
beamline_name = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME, "i06")
beamlineutil=BeamlineFunctionClass(beamline_name)

if beamline_name=="i06-1":
    rootPV = "BL06J-MO-FSCAN-02"
elif beamline_name=="i06":
    rootPV = "BL06I-MO-FSCAN-02"
else:
    raise ValueError("'rootPV' is NOT specified!")

fastScanElementCounter="iduFastScanElementCounter"
# create Fast Energy Scan Controller for EPICS
fesController = FastEnergyScanControlClass("fesController", rootPV);
zacmode = FastEnergyScanIDModeClass("zacmode", fesController);
# configure data collection object
if beamline_name =="i06-1":
    fesData = EpicsWaveformDeviceClass("fesData", rootPV, ['C1','C2', 'C3', 'C4', 'iduenergy', 'pgmenergy', 'C5', 'C6'], ['idio', 'ifio', 'ifioft', 'ifiofb'],elementCounter=fastScanElementCounter);
elif beamline_name =="i06":
    fesData = EpicsWaveformDeviceClass("fesData", rootPV, ['C1','C2', 'C3', 'C4', 'iduenergy', 'pgmenergy', 'ROI1', 'ROI2'], ['roi1io1', 'roi1io2', 'roi2io1', 'roi2io2'],elementCounter=fastScanElementCounter);
    
    if ENABLE_KB_RASTERING:
        #configure KB Mirror rastering
        KEYSIGHT_KB_Rastering_Control_PV="BL06I-EA-SGEN-01:PERIOD"
        fesController.setKBRasteringControlPV(KEYSIGHT_KB_Rastering_Control_PV)
    fesController.setKBRastering(ENABLE_KB_RASTERING) 

    ### configure which area detector to use in zacscan           
    from __main__ import zacmedipix  # @UnresolvedImport
    fesController.setAreaDetector(zacmedipix)
fastEnergy = FastEnergyDeviceClass("fastEnergy", fesController, fesData)

def zacscan(startEnergy, endEnergy, scanTime, pointTime):
    try:
        uuu.backupDefaults()
        if beamline_name=="i06-1":
            uuu.removeDefaults(['ca61sr', 'ca62sr','ca63sr','ca64sr','ca65sr','ca66sr'])
        beamlineutil.stopArchiving()
        fastEnergy.cvscan(startEnergy, endEnergy, scanTime, pointTime)
        beamlineutil.registerFileForArchiving( beamlineutil.getLastScanFile() )
        beamlineutil.restoreArchiving()
        uuu.restoreDefaults()        
    except :
        errortype, exception, traceback = sys.exc_info()
        logger.fullLog(None, "Error in zacscan", errortype, exception , traceback, False)        

alias("zacscan")

def zacstop():
    try:
        fastEnergy.stop()
        beamlineutil.restoreArchiving()
        InterfaceProvider.getCommandAborter().abortCommands()
    except :
        errortype, exception, traceback = sys.exc_info()
        logger.fullLog(None, "Error in stopping the zacscan ", errortype, exception , traceback, False)       

alias("zacstop")

from gda.jython.commands.ScannableCommands import pscan

"""
    An External function to run the I06 energy constant velocity scan by using the  FastEnergyScanClass class
    This method is for debug only and should be replaced by the above zacscan command 
"""
def fastscan(startEnergy, endEnergy, scanTime, pointTime):
    fesData.reset()
    fesController.setEnergyRange(startEnergy, endEnergy)
    fesController.setTime(scanTime, pointTime)
    fesController.setIDMode(1)

    if pointTime > 2.0:
        fastEnergy.setDelay(pointTime/2.0)
    elif pointTime>0.5:
        fastEnergy.setDelay(pointTime/5.0)
    else:
        fastEnergy.setDelay(pointTime/10.0)
        
    
    numPoint = fesController.getNumberOfPoint()
    step=1.0*(endEnergy - startEnergy)/numPoint
    
#    scan timer 0 scanTime pointTime fastEnergy 1 sdd 10
#    pscan fastEnergy 0 1 numPoint fesData 0 1;
    pscan([fastEnergy,0,1,numPoint,fesData,0,1])


