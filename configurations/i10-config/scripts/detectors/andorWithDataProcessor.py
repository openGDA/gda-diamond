'''
Created on 5 Apr 2018

@author: fy65
'''
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from utils.ExceptionLogs import localStation_exception
import sys
from gda.jython.commands.GeneralCommands import alias

try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf
    global andor1det, andor1det_for_snaps, andor1GV12det, andor1GV12det_for_snaps #NOTE require Andor bean definition which is missing from I10???

    # the andor has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    andor = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'andor', andor1det, None, andor1det_for_snaps, [],
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    #from scannable.adbase import ADTemperature
    #andortemp = ADTemperature('andortemp', andor1.getCollectionStrategy().getAdBase())
    #from scannable.andor import andor_trigger_output_enable, andor_trigger_output_disable
    #alias('andor_trigger_output_disable')
    #alias('andor_trigger_output_enable')
    #andor_trigger_output_enable()

    andorGV12 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'andorGV12', andor1GV12det, None, andor1GV12det_for_snaps, [],
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    def andorGV12openDelay(t_seconds = None):
        """Get or set the shutter close delay (in seconds) for the andor"""
        if t_seconds == None:
            return andor1GV12det.getCollectionStrategy().getShutterOpenDelay()
        andor1GV12det.getCollectionStrategy().setShutterOpenDelay(t_seconds)
    
    def andorGV12closeDelay(t_seconds = None):
        """Get or set the shutter close delay (in seconds) for the andor"""
        if t_seconds == None:
            return andor1GV12det.getCollectionStrategy().getShutterCloseDelay()
        andor1GV12det.getCollectionStrategy().setShutterCloseDelay(t_seconds)
    
    alias('andorGV12openDelay')
    alias('andorGV12closeDelay')
    
except:
    localStation_exception(sys.exc_info(), "creating andor & andorGV12 objects")