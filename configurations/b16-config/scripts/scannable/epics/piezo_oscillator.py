from gda.data.nexus.extractor import NexusGroupData
from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.device.detector import NXDetectorData, NexusDetector
from gda.device.scannable import ScannableMotionBase
from gda.epics import LazyPVFactory
from org.eclipse.january.dataset import DatasetFactory
from threading import Thread, Event
import time

class OscillatorController:
    
    def set_amplitude(self, amplitude):
        raise NotImplementedError
    
    def get_amplitude(self):
        raise NotImplementedError
    
    def set_period(self, period):
        raise NotImplementedError
    
    def oscillate(self):
        raise NotImplementedError
    
    def done(self):
        raise NotImplementedError


class EpicsOscillatorController(OscillatorController):
    def __init__(self, pv_base):
        pv_base = pv_base if pv_base.endswith(":") else pv_base + ":"
        self.displacement_pv = LazyPVFactory.newIntegerPV(pv_base + "AMPLITUDE")
        self.period_pv = LazyPVFactory.newIntegerPV(pv_base + "PERIOD")
        self.cycles_pv = LazyPVFactory.newIntegerPV(pv_base + "CYCLES")
        self.oscillate_pv = LazyPVFactory.newIntegerPV(pv_base + "RUN")
        self.done_pv = LazyPVFactory.newIntegerPV(pv_base + "DONE")
        self.done_pv.addMonitorListener(self.done_monitor)
        
        self.steady_state = Event()
        self.failed = False

    def set_amplitude(self, amplitude):
        self.displacement_pv.putWait(int(amplitude))
    
    def get_amplitude(self):
        return self.displacement_pv.get()
    
    def set_period(self, period):
        self.period_pv.putWait(period)
    
    def oscillate(self):
        self.steady_state.clear()
        
        self.oscillate_pv.putNoWait(1)
        
        # period (in ms) multiplied by number of oscillations multiplied by 3 to be generous
        wait_time = 3 * self.cycles_pv.get() * self.period_pv.get() / 1000
        Thread(target=lambda: self.start_timeout(wait_time))
    
    def done(self):
        if self.failed:
            raise DeviceException("Oscillation did not complete")
        
        return self.steady_state.is_set()
    
    def done_monitor(self, event):
        if self.steady_state.is_set():
            return
        
        if self.done_pv.get() == 1:
            self.steady_state.set()
    
    def start_timeout(self, wait_time):
        if not self.steady_state.wait(wait_time):
            self.failed = True
            self.steady_state.set()


class PiezoOscillator(ScannableMotionBase):
    def __init__(self, name, controller):
        self.name = name
        self.controller = controller
    
    def asynchronousMoveTo(self, displacement):
        self.controller.set_amplitude(displacement)
        self.controller.oscillate()
    
    def rawGetPosition(self):
        return self.controller.get_amplitude()
    
    def isBusy(self):
        return not self.controller.done()



class OscillationDetector(DetectorBase, NexusDetector):

    def __init__(self, name, pv_base):
        
        pv_base = pv_base if pv_base.endswith(":") else pv_base + ":"
        self.data_pv = LazyPVFactory.newDoubleArrayPV(pv_base + "POSDATA")
        self.time_pv = LazyPVFactory.newIntegerArrayPV(pv_base + "TIMEDATA")
        self.size_pv = LazyPVFactory.newIntegerPV(pv_base + "SIZEDATA")
        
        self.name = name
        self.setExtraNames(["oscillation", "timestamp"])
        self.setOutputFormat(["%5.5g", "%5.5g", "%5d"])

    def readout(self):
        
        data_size = self.size_pv.get()
        data = self.data_pv.get(data_size)
        timestamp = DatasetFactory.createFromObject(self.time_pv.get(data_size))
        
        detector_data = NXDetectorData(self.getExtraNames(), self.getOutputFormat(), self.getName())
        tree = detector_data.getDetTree(self.getName())
        oscillation_data = DatasetFactory.createFromObject(data)
        NXDetectorData.addData(tree, "oscillation", NexusGroupData.createFromDataset(oscillation_data), "nm", 1)
        NXDetectorData.addData(tree, "timestamp", NexusGroupData.createFromDataset(timestamp), "ms", 1)
        
        return detector_data

    def getStatus(self):
        return Detector.IDLE

    def collectData(self):
        pass
    
    def createsOwnFiles(self):
        return False

class OscillationDetectorWrapper(DetectorBase, NexusDetector):
    """
    Acquires while oscillating.
    The oscillating stage needs to be configured already (the presently set values are used)
    """
    def __init__(self, det, osc):
        self.det = det
        self.osc = osc
        
        self.name = self.det.name + "_osc"
        self.setExtraNames(self.det.extraNames)
        self.setOutputFormat(self.det.outputFormat)
        
    def collectData(self):
        self.osc.asynchronousMoveTo(self.osc.getPosition())
        self.det.collectData()
    
    def readout(self):
        return self.det.readout()
    
    def createsOwnFiles(self):
        return self.det.createsOwnFiles()
    
    def getStatus(self):
        if self.osc.isBusy() or self.det.isBusy():
            return Detector.BUSY
        return self.det.getStatus()

class MotorWithBackgroundOscillations(ScannableMotionBase):
    '''
    Moves motor, then starts oscillation.
    Only busy while motor is busy. This means that during a scan,
    the detectors would collect while the oscillation is ongoing.
    '''
    def __init__(self, sm, osc):
        self.sm = sm
        self.osc = osc
        self.setName(sm.getName() + "_osc")
        self._busy = False

    def rawAsynchronousMoveTo(self, position):
        while self.osc.isBusy():
            # still performing previous oscillation!
            time.sleep(0.01)
        self._busy = True
        self.sm.moveTo(position)
        time_to_start_oscillation = 1.5
        Thread(target=self.turn_off_busy_after, args=(time_to_start_oscillation,)).start()
        self.osc.asynchronousMoveTo(self.osc.getPosition())
    
    def turn_off_busy_after(self, t_s):
        time.sleep(t_s)
        self._busy = False
    
    def rawGetPosition(self):
        return self.sm.getPosition()
    
    def isBusy(self):
        return self._busy

def create_osc_devices(name, pvbase):
    osc = PiezoOscillator(name + "_osc", EpicsOscillatorController(pvbase))
    det = OscillationDetector(name + "_det", pvbase)
    return (osc, det)