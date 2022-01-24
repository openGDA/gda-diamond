# scan vspeed profile(10, 20, 40, 1) t 0 .1 point 0 1 clock epoch dt
import time

from gdascripts.scannable.dummy import SingleInputDummy
import scannable.shutter


from gdascripts.scannable.timerelated import *
from gdascripts.scannable.dummy import SingleInputDummy
from gda.device.scannable import ScannableBase
from scannable.copiedFromb16_SetPvAndWaitForCallback import SetPvAndWaitForCallback
from gda.epics import CAClient

class VariableSpeedMotor(SetPvAndWaitForCallback):
    """Simply drives an analogue PV to desired voltage, but makes sure it
    ends up at 0.
    """    
    def atCommandFailure(self):
        self.stop()

    def stop(self):
        print self.name + " stopping motor"
        self.moveTo(0)


class TimeSinceLineStartAccurate(ScannableBase):
    """
    Returns the time since the last scan started. When driven to a time will remain busy until this time has elapsed.
    """
    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%6.2f']
        self.level = 7
        
        self._time_at_line_start = 0
        self.deltaTime = 0

    def atScanLineStart(self):
        self._time_at_line_start = time.time()  

    def getPosition(self):
        return time.time() - self._time_at_line_start

    def asynchronousMoveTo(self, target_time):
        absolute_target = self._time_at_line_start + target_time
        delta_time = absolute_target - time.time()
        if delta_time > 0:
            time.sleep(delta_time)

    def stop(self):
        self._time_at_line_start = 0

    def isBusy(self):
        return False


class Pilat2StateRestorer(ScannableBase):
    
    def __init__(self):
        self.inputNames = []
        self.extraNames = []
        self.outputFormat = []
        self.name = 'pil2M_state_restorer'
        self._numImagesPv = CAClient("BL07I-EA-PILAT-02:CAM:NumImages")
        self._imageModePv = CAClient("BL07I-EA-PILAT-02:CAM:ImageMode")
        self._nextFileNumberPv = CAClient("BL07I-EA-PILAT-02:CAM:FileNumber")
                
        self._numImagesPv.configure()
        self._imageModePv.configure()
        self._nextFileNumberPv.configure()
        
        self._initialFileNumber = None
        

    def getPosition(self):
        return
    
    def isBusy(self):
        return False
    
    def waitWhileBusy(self):
        return
    
    def atScanStart(self):
        self._initialFileNumber = int(self._nextFileNumberPv.caget())
    
    def atScanEnd(self):
        self.restoreState()
    
    def stop(self):
        self.restoreState()
        
    def atCommandFailure(self):
        self.restoreState()
        
    def restoreState(self):
        self._numImagesPv.caput(1)
        self._imageModePv.caput(0)  # Single
        self._nextFileNumberPv.caput(self._initialFileNumber)





def profile(n_delay, n_ramp, n_hold, v_max):
    profile = []
    profile += [0] * n_delay
    profile += [v_max * i / float(n_ramp) for i in range(0, n_ramp)]
    profile += [v_max] * n_hold
    profile += [v_max * i / float(n_ramp) for i in range(n_ramp, 0, -1)]
    profile += [0] * n_delay
    return tuple(profile)


vspeed=VariableSpeedMotor('vspeed', 'BL07I-EA-USER-01:AO1')
point = SingleInputDummy('point')
t = TimeSinceLineStartAccurate('t')
fsscan = scannable.shutter.ScanStartToggler('fsscan', fs)  #@UndefinedVariable
pil2mrestorer = Pilat2StateRestorer()

t.outputFormat=['%6.4f']
dt.outputFormat=['%6.4f']
epoch.outputFormat = ['%.4f']
clock.outputFormat=['%i', '%i', '%.4f']

#scan vspeed profile(10, 20, 40, 1) t 0 .1 point 0 1 clock epoch dt pil2multi .1 pil2mrestorer


