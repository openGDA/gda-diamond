from gda.device.detector import DetectorBase
#from gda.device.scannable import ScannableBase
from gdascripts.scannable.epics.PvManager import PvManager
from gda.epics import LazyPVFactory, CAClient

CATIMEOUT = 5

def _caputwait(pvstring, value):
    cac=CAClient(pvstring)
    cac.configure()
    cac.caput(CATIMEOUT, value)
    cac.clearup()

class DxpSingleChannelRoiOnly(DetectorBase):
    
    def __init__(self, name, pvroot, roi_indexes=[0, 1, 2], channel=1):

        self.name = name
        self.pvroot = pvroot
        self.roi_indexes = roi_indexes
        self.channel = channel
        
        self.inputNames = []
        self.extraNames = ['acquire_time'] + ['roi' + str(i) for i in roi_indexes]
        self.level = 9
        self.outputFormat = ['%.2f'] +['%i'] * len(roi_indexes)
        
        self._pvs = PvManager(pvroot=pvroot)
        self._pv_erase_and_start = LazyPVFactory.newBooleanFromEnumPV(pvroot + 'EraseStart')
        self.configure()
        
    def configure(self):
        dxp = 'DXP%i:' % self.channel
        self._caputwait('PresetMode', 1) # real time
        self._caputwait(dxp + 'TriggerThreshold', 1) # kEv
        self._caputwait(dxp + 'BaselineThreshold', 1) # kEv
        self._caputwait(dxp + 'EnergyThreshold', 0) # kEv
        self._caputwait('MCA1.NUSE', 16384)
        # bin width = 10
        # drange = 47200
        # cal energy = 5900
        # peak time = 0
        # status update time = .1
        # data readout time = .1
    
    def prepareForCollection(self):
        self._pvs['PresetReal'].caput(CATIMEOUT, float(self.collectionTime))
        
    def isBusy(self):
        return bool(self._pvs['Acquiring'].caget())

    def collectData(self):
        self._pv_erase_and_start.startPutCallback(True)
        
    def waitWhileBusy(self):
        self._pv_erase_and_start.waitForCallback()
                        
    def readout(self):
        realtime = self._pvs['PresetReal'].caget()
        return [realtime] + [self._read_roi_sum(self.channel, i) for i in self.roi_indexes]

    def stop(self):
        self._pvs['StopAll'].caput(1)
        self._pv_erase_and_start.cancelPendingCallback()
     
    def _read_roi_sum(self, channel, roi):
        """channels are numbered from 1, and rois from 0"""
        return int(float(self._pvs['MCA' + str(channel) + '.R' + str(roi)].caget()))
    
    def _caputwait(self, field, value):
        _caputwait(self.pvroot + field, value)
        