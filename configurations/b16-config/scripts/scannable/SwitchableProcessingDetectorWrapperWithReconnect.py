from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from gda.epics import CAClient

#Written to be used by the PSL SCMOS camera, which has a issue on the Controls side that causes acquisitions to take an increasing amount of time
#Detector acquires quickly following a reconnect, so we call reconnect before acquiring.
class SwitchableProcessingDetectorWrapperWithReconnect(SwitchableHardwareTriggerableProcessingDetectorWrapper):

    def __init__(self, name,
                detector,
                hardware_triggered_detector,
                detector_for_snaps,
                reconnectPv,
                processors=[],
                panel_name=None,
                toreplace=None,
                replacement=None,
                iFileLoader=None,
                root_datadir=None,
                fileLoadTimout=None,
                printNfsTimes=False,
                returnPathAsImageNumberOnly=False,
                panel_name_rcp=None,
                return_performance_metrics=False,
                array_monitor_for_hardware_triggering=None):

        SwitchableHardwareTriggerableProcessingDetectorWrapper.__init__(self, name,
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
                array_monitor_for_hardware_triggering)

        self.caClient = CAClient(reconnectPv)
        self.caClient.configure()
        self.reconnectTimeout = 10

    def prepareForAcquisition(self, time):
        SwitchableHardwareTriggerableProcessingDetectorWrapper.prepareForAcquisition(self, time)
        self.caClient.caput(self.reconnectTimeout, 1)

    def atScanStart(self):
        SwitchableHardwareTriggerableProcessingDetectorWrapper.atScanStart(self)
        self.caClient.caput(self.reconnectTimeout, 1)
