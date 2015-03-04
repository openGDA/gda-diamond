"""
Scannable Oxford Diffraction Intelligent Temperature Controller (High Field
Magnet), for use with GDA at Diamond Light Source
"""

from gda.device.scannable import ScannableMotionBase
from high_field_magnet.device.intelligentTemperatureController import IntelligentTemperatureController
from threading import Timer

"""
    <OxInstCryojet desc="Magnet Intelligent Temperature Controller J1" name="MAGJ1.ITCJ1">
        <PGAIN_SET desc="set pid p" pv="BL10J-EA-TCTRL-01:P:SET" ro="false" type="pv"/>
        <IGAIN_SET desc="set pid i" pv="BL10J-EA-TCTRL-01:I:SET" ro="false" type="pv"/>
        <DGAIN_SET desc="set pid d" pv="BL10J-EA-TCTRL-01:D:SET" ro="false" type="pv"/>
        <TEMP_SET desc="set target temp" pv="BL10J-EA-TCTRL-01:TTEMP:SET" ro="false" type="pv"/>
        <SENSOR_TEMP desc="get sensor temp" pv="BL10J-EA-TCTRL-01:STEMP" ro="true" type="pv"/>
        <DISABLE desc="disable comms" pv="BL10J-EA-TCTRL-01:DISABLE" ro="false" type="binary"/>
    </OxInstCryojet>
"""

class IntelligentTemperatureControllerScannable(ScannableMotionBase): 
    """IntelligentTemperatureControllerScannable:
    `pos scn` returns setpoint and current sensor temperature
    `pos scn X` sets a new setpoint and returns it and the final sensor reading
Extensions:
    `scn.temp_tolerance=X` is the allowable temperature deviation from the setpoint
    `scn.stable_time_sec=X` is the time it needs to be in tolerance for, 0 by default
    `scn.verbose=True` prints out extra debugging info (at 10Hz) defaults to False"""

    def __init__(self, name, pvroot, temp_tolerance, stable_time_sec=0, stop_sets_setpoint_to_readback=False):
        self.name = name
        
        self.itc = IntelligentTemperatureController(pvroot)
        self.temp_tolerance = temp_tolerance
        self.stable_time_sec = stable_time_sec
        self.stop_sets_setpoint_to_readback = stop_sets_setpoint_to_readback
        
        self.setpoint = 0
        self.stable = True
        self.verbose = False
        self.hold_timer = self._timer_factory()
        
        self.inputNames = [name]
        self.extraNames = ['sensor_temp']
        self.outputFormat = ['%f', '%f']

    def __repr__(self):
        return "IntelligentTemperatureControllerScannable(%r, %r, %r, %r)" % (
            self.name, self.itc.pvs.pvroot, self.temp_tolerance, self.stable_time_sec)

    def __str__(self):
        return "setpoint=%f, sensor=%f" % self.getPosition()

    def _timer_factory(self):
        return Timer(self.stable_time_sec, self._timer_completed)

    def _timer_completed(self):
        self.stable = True
        if self.verbose:
            print "IntelligentTemperatureControllerScannable: Hold timer finished..."

    def getPosition(self):
        return (self.itc.getTempSetPoint(),
                self.itc.getTempSensor())

    def rawAsynchronousMoveTo(self,setpoint):
        if self.verbose:
            print "IntelligentTemperatureControllerScannable: Moving to %r" % setpoint
        self.setpoint = setpoint
        self.itc.setTempSetPoint(setpoint)
        self.stable = False
        self.hold_timer.cancel()

    def stop(self):
        if self.stop_sets_setpoint_to_readback:
            self.rawAsynchronousMoveTo(self.itc.getTempSensor())
        self.stable = True
        if self.verbose:
            print "IntelligentTemperatureControllerScannable: Stopped"

    def isBusy(self):
        # Note that we rely on isBusy being called often enough that the
        # hold_timer will be cancelled before it triggers if the temperature
        # goes out of range before the end of the hold timer. Only when the
        # temperature is stable will this scannable stop being busy. 
        if not self.stable:
            dtemp = self.setpoint - self.itc.getTempSensor()
            if abs(dtemp) > self.temp_tolerance:
                self.hold_timer.cancel()
                if self.verbose:
                    print "IntelligentTemperatureControllerScannable: temperature differential %f greater than %f from %f" % (dtemp, self.temp_tolerance, self.setpoint)
            elif not self.hold_timer.isAlive():
                self.hold_timer = self._timer_factory()
                self.hold_timer.start()
                if self.verbose:
                    print "IntelligentTemperatureControllerScannable: Hold timer started..."
            else:
                if self.verbose:
                    print "IntelligentTemperatureControllerScannable: Holding..."
            return True
        
        if self.verbose:
            print "IntelligentTemperatureControllerScannable: No longer busy"
        return False
