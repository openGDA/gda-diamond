from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from gda.device import DeviceException

class NxProcessingDetectorWrapper(SwitchableHardwareTriggerableProcessingDetectorWrapper):

    def __init__( self,
                name,
                detector,
                hardware_triggered_detector,
                detector_for_snaps,
                processors = [],
                panel_name = None,
                toreplace = None,
                replacement = None,
                iFileLoader = None,
                root_datadir = None,
                fileLoadTimout = None,
                printNfsTimes = False,
                returnPathAsImageNumberOnly = False,
                panel_name_rcp = None,
                return_performance_metrics = False,
                array_monitor_for_hardware_triggering = None):

        SwitchableHardwareTriggerableProcessingDetectorWrapper.__init__( self,
                name,
                detector,
                hardware_triggered_detector,
                detector_for_snaps,
                processors,
                panel_name,
                toreplace,
                replacement,
                iFileLoader,
                root_datadir,
                fileLoadTimout,
                printNfsTimes,
                returnPathAsImageNumberOnly,
                panel_name_rcp,
                return_performance_metrics,
                array_monitor_for_hardware_triggering )

        self.lastReadout = None

    def atScanEnd(self):
        SwitchableHardwareTriggerableProcessingDetectorWrapper.atScanEnd(self)

    def getExtraNames(self): # Replace ExtraName 't' with 'count_time'
        return ['count_time'] + SwitchableHardwareTriggerableProcessingDetectorWrapper.getExtraNames(self)[1:]

    def _readout(self):
        #we need "something" from _readout even if a scan is canceled (used to get the filepath)
        #this is perhaps really terrible and could hide problems
        try:
            out = SwitchableHardwareTriggerableProcessingDetectorWrapper._readout(self)
            # MBB Should ^^^ be vvv ?
            #out = SwitchableHardwareTriggerableProcessingDetectorWrapper.getPositionCallable(self).call()
            self.lastReadout = out
            return out
        except DeviceException:
            if self.lastReadout == None:
                raise #this is getting silly
            return self.lastReadout
