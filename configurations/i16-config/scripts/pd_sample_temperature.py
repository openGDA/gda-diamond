"""
Sample temperature controller for multiple temperature controllers
  read temperatures
  set temperature, ramp rate, power, PID values
e.g.
from sample_temperature import TemperatureController
tcontrol_id = pd_offset.Offset('tcontrol_id')
tcontrol = TemperatureController('tcontrol', tcontrol_id)
tcontrol = TemperatureController('tcontrol')
tset = tcontrol.tset_device()
Ta = tcontrol.Ta_device()
Tb = tcontrol.Tb_device()
Tsample = tcontrol.Tsample_device('sample_temperature')
twait = tcontrol.twait_device()
tchannel = tcontrol.Tchannel_device('tchannel')

pos tcontrol 340  # selects old lakeshore
pos tset 300 # sets temperature to 300 K
pos Ta # reads temperature sensor
pos twait [300, 0.5]  # sets [temperature, tolerance], waits for sample sensor to reach setpoint

tcontrol.ramp(value)  # set the ramp rate
tcontrol.rame(0)  # turn off the temperature ramp
tcontrol.heater(-1)  # turn on heater full power
tcontrol.heater(0)  # turn off heater

Available controllers:
pos tcontrol 'lakeshore 340' # old lakeshore
pos tcontrol 'lakeshore 336' # new laksshore
pos tcontrol 'cryostream 700' # gas jet cryostream

Old scannable device "tset":
/dls_sw/i16/software/gda/config/scripts/pd_LS340control.py
/dls_sw/i16/scripts/devices/pd_cryostream700.py


By Dan Porter, BLI16
2023
"""

from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from misc_functions import caput, caget, frange
from time import sleep
import scisoftpy as dnp

#### EPICS device names ####
NAMES = 'names'
SET = 'set'
HEAT = 'heat range'
RATE = 'ramp rate'
RAMP = 'ramp on'
RHEAT = 'read heater'
RTA = 'read temperature A'
RTB = 'read temperature B'
RTC = 'read temperature C'
RTD = 'read temperature D'
RTS = 'sample temperature'
HEAT_OPT = 'heater options'
PID = 'set PID'
RP = 'read PID'
CHAN = 'Control channel'
CH_OPT = 'channel options'


CONTROLLERS = {
    'Lakeshore 340': {
        NAMES: ['lakeshore 340', '340', 'old lakeshore'],
        SET: 'BL16I-EA-LS340-01:SETP_S',
        HEAT: 'BL16I-EA-LS340-01:RANGE_S', # 0, 1, 2, 3, 4, 5
        RATE: 'BL16I-EA-LS340-01:RAMP_S',
        RAMP: 'BL16I-EA-LS340-01:RAMPST_S',
        RHEAT: 'BL16I-EA-LS340-01:HTR',
        RTA: 'BL16I-EA-LS340-01:KRDG0',
        RTB: 'BL16I-EA-LS340-01:KRDG1',
        RTC: 'BL16I-EA-LS340-01:KRDG2',
        RTD: 'BL16I-EA-LS340-01:KRDG3',
        RTS: 'BL16I-EA-LS340-01:KRDG0',
        CHAN: 'BL16I-EA-LS340-01:ASYN.AOUT',  # 'CSET 1,A', 'CSET 1,B', 'CSET 1,C', 'CSET 1,D'
        CH_OPT: ['CSET 1,A', 'CSET 1,B', 'CSET 1,C', 'CSET 1,D'],
        HEAT_OPT: ['0', '1', '2', '3', '4', '5'],
        PID: 'BL16I-EA-LS340-01:%s_S',  #% 'P', 'I', 'D'
        RP: 'BL16I-EA-LS340-01:%s',  #% 'P', 'I', 'D'
    },
    'Lakeshore 336': {
        NAMES: ['lakeshore 336', '336', 'new lakeshore'],
        SET: 'BL16I-EA-LS336-01:SETP_S1',
        HEAT: 'BL16I-EA-LS336-01:RANGE_S1', # 'Off', 'Low', 'Medium', 'High'
        RATE: 'BL16I-EA-LS336-01:RAMP_S1',
        RAMP: 'BL16I-EA-LS336-01:RAMPST_S1',
        RHEAT: 'BL16I-EA-LS336-01:HTR1',
        RTA: 'BL16I-EA-LS336-01:KRDG0',
        RTB: 'BL16I-EA-LS336-01:KRDG1',
        RTC: 'BL16I-EA-LS336-01:KRDG2',
        RTD: 'BL16I-EA-LS336-01:KRDG3',
        RTS: 'BL16I-EA-LS336-01:KRDG0',
        CHAN: 'BL16I-EA-LS336-01:OMINPUT_S1',  # 'None', 'Input 1', 'Input 2', 'Input 3', 'Input 4'
        CH_OPT: ['None', 'Input 1', 'Input 2', 'Input 3', 'Input 4'],
        HEAT_OPT: ['Off', 'Low', 'Medium', 'High'],
        PID: 'BL16I-EA-LS336-01:%s_S1',  #% 'P', 'I', 'D'
        RP: 'BL16I-EA-LS336-01:%s1',  #% 'P', 'I', 'D'
    },
    'Cryostream Plus 700': {
        NAMES: ['cryostream plus 700', 'cryostream', 'cryostream 700', 'gasjet', 'tgas', '700'],
        SET: 'BL16I-EA-TEMPC-02:RTEMP',
        HEAT: 'BL16I-EA-TEMPC-02:RRATE',
        RATE: 'BL16I-EA-TEMPC-02:RRATE',
        RAMP: 'BL16I-EA-TEMPC-02:RAMP.PROC',
        RHEAT: 'BL16I-EA-TEMPC-02:TARGETTEMP',
        RTA: 'BL16I-EA-TEMPC-02:TEMP',
        RTB: None,
        RTC: None,
        RTD: None,
        RTS: 'BL16I-EA-TEMPC-02:TEMP',
        CH_OPT: None,
        CHAN: None,
        HEAT_OPT: ['0', '360'],
        PID: None,
        RP: None,
    },
}
CONTROLLER_NAMES = list(CONTROLLERS.keys())


class TemperatureController(ScannableMotionBase):
    """
    Sample temperature controller for multiple temperature controllers
    ***Currently untested for cryostream 700***

    Instatiate:
        from sample_temperature import TemperatureController
        tcontrol_id = pd_offset.Offset('tcontrol_id')
        tcontrol = TemperatureController('tcontrol', tcontrol_id)
        tset = tcontrol.tset_device('tset')
        Ta = tcontrol.Ta_device('Ta')
        Tb = tcontrol.Tb_device('Tb')
        Tc = tcontrol.Ta_device('Tc')
        Td = tcontrol.Tb_device('Td')
        Tsample = tcontrol.Tsample_device('sample_temperature')
        twait = tcontol.twait_device('twait')

    Usage:
        tcontrol.set_device('Lakeshore 340')
        pos tcontrol 340  # selects old lakeshore
        pos tset 300 # sets temperature to 300 K
        pos Ta # reads temperature sensor
        pos Tsample  # reads Ta or Tb (use tcontrol.set_tsample('a'))
        pos twait [300, 0.5]  # sets [temperature, tolerance], waits for sample sensor to reach setpoint

    Additional methods:
        tcontrolinfo()  # print all current sensor outputs
        tcontrol.options()  # print available controllers
        tcontrol.set_tsample('Tb')  # Sets Tsample pointer
        tcontrol.set_temperature_setpoint(300)  # sets temperature setpoint (same as tset)
        tcontrol.ramp(value)  # turns ramp on or off, sets rate
        tcontrol.heater()  # returns heater %
        tcontrol.heater('High')  # sets heater power.
        tcontrol.control_chan(channel_string) sets control channel (1-4), ('A', 'B', 'C' or 'D')
        tcontrol.pid(): read PID values
        tcontrol.pid([P,I,D]): set PID values
        tcontrol.warmup(): Sets ramp OFF, setpoints=300K

    Available controllers:
        pos tcontrol 'lakeshore 340' # old lakeshore
        pos tcontrol 'lakeshore 336' # new laksshore
        pos tcontrol 'cryostream 700' # gas jet cryostream

    code defined in: /dls_sw/scripts/i16_gda_functions/sample_temperature.py
    """
    def __init__(self, name, pd_device_index):
        """What's up Doc?"""

        self.device = None
        self.pd_device_index = pd_device_index
        self.pvs = {}
        self._set_from_index()

        self.setName(name)
        self.setInputNames(['Tcontrol_id'])
        self.setExtraNames(['Tcontrol_device'])
        self.Units=['']
        self.setOutputFormat(['%.0f', '%s'])
        self.setLevel(5)

        self._tset_device = None
        self._twait_device = None
        self._Ta_device = None
        self._Tb_device = None
        self._Tc_device = None
        self._Td_device = None
        self._Ts_device = None
        self._Th_device = None

    "==================== Controller Methods ======================="

    def _get_pv(self, name):
        """Return PV string from label"""
        return self.pvs[name]

    def get_value(self, name):
        """Return PV string"""
        return caget(self._get_pv(name))

    def set_value(self, name, value):
        """caput(_get_pv(name))"""
        caput(self._get_pv(name), value)

    def controllers(self):
        print('Available controllers:')
        print('\n'.join(['   %d: %s' % (i, name) for i, name in enumerate(CONTROLLER_NAMES)]))

    def info(self):
        """Display the current settings"""
        print('Temperature controller: %s : %s' % (self.name, self.device))
        print(' PVs:')
        print('  set: %s' % self.get_value(SET))
        print('  heatrange: %s' % self.get_value(SET))
        print('  ramprate: %s' % self.get_value(RATE))
        print('  rampon: %s' % self.get_value(RAMP))
        print('  heater: %s' % self.get_value(RHEAT))
        print('  Ta: %s' % self.get_value(RTA))
        print('  Tb: %s' % self.get_value(RTB))
        print('  Tc: %s' % self.get_value(RTC))
        print('  Td: %s' % self.get_value(RTD))
        print('  Tsample: %s' % self.get_value(RTS))

    def options(self):
        """Display available controllers"""
        print('%14s: %s' % ('Device name', 'accepted names'))
        for cname, controller in CONTROLLERS.items():
            print('%14s: %s' % (cname, controller[NAMES]))

    def _set_from_index(self):
        """Set temperature controller from current index"""
        index = int(self.pd_device_index())
        device_name = CONTROLLER_NAMES[index]
        self.set_device(device_name)

    def set_device(self, device_index='336'):
        """Sets the temperature controller, options: '336', '340', '700'"""
        try:
            # value given
            if device_index > 300:
                device_name = str(device_index).lower()
            else:
                idx = int(device_index % len(CONTROLLER_NAMES))
                device_name = CONTROLLER_NAMES[idx]
        except TypeError:
            # str given
            device_name = str(device_index).lower()

        for cname, controller in CONTROLLERS.items():
            if device_name.lower() in controller[NAMES]:
                self.pvs = controller.copy()
                self.device = cname
                self.pd_device_index(CONTROLLER_NAMES.index(cname))
                print('%s pvs set for %s' % (self.name, cname))
                return
        print('No controller set, keeping as %s' % self.device)

    def set_tsample(self, new_tsample='Tb'):
        """Switch the PVs of Tsample (doesn't change control channel)"""
        if isinstance(new_tsample, ControllerReader):
            self.pvs[RTS] = new_sample.sensor
        else:
            if 'b' in new_tsample.lower():
                self.pvs[RTS] = self.pvs[RTB]
            elif 'c' in new_tsample.lower():
                self.pvs[RTS] = self.pvs[RTC]
            elif 'd' in new_tsample.lower():
                self.pvs[RTS] = self.pvs[RTD]
            else:
                self.pvs[RTS] = self.pvs[RTA]

    "==================== Scannable Methods ========================="

    def getPosition(self):
        return self.pd_device_index(), self.device

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, controller_name):
        self.set_device(controller_name)

    "==================== Device Instatiation ======================="

    def tset_device(self, name='tset', unitstring='K', formatstring='%5.2f'):
        """Return instatiated tset object for current controller"""
        self._tset_device = ControllerSetter(name, self, unitstring, formatstring)
        return self._tset_device

    def twait_device(self, name='twait', setter=None, reader=None):
        """Return instatiated tset object for current controller"""
        if setter is None:
            setter = self._tset_device()
        if reader is None:
            reader = self._Ts_device()
        self._twait_device = TemperatureWaiter(name, setter, reader)
        return self._twait_device

    def Ta_device(self, name='Ta', unitstring='K', formatstring='%5.2f'):
        """Return instatiated Tsample linked to this controller"""
        return ControllerReader(name, self, RTA, unitstring, formatstring)

    def Tb_device(self, name='Tb', unitstring='K', formatstring='%5.2f'):
        """Return instatiated Tsample linked to this controller"""
        return ControllerReader(name, self, RTB, unitstring, formatstring)

    def Tc_device(self, name='Tc', unitstring='K', formatstring='%5.2f'):
        """Return instatiated Tsample linked to this controller"""
        return ControllerReader(name, self, RTC, unitstring, formatstring)

    def Td_device(self, name='Td', unitstring='K', formatstring='%5.2f'):
        """Return instatiated Td object linked to this controller"""
        return ControllerReader(name, self, RTD, unitstring, formatstring)

    def Tsample_device(self, name='Tsample', unitstring='K', formatstring='%5.2f'):
        """Return instatiated Tsample linked to this controller"""
        tsample = ControllerReader(name, self, RTS, unitstring, formatstring)
        tsample.__doc__ += "Change Tsample using tcontrol.set_tsample(Tb)\n"
        return tsample

    def Theater_device(self, name='Theat', unitstring='%', formatstring='%5.2f'):
        """Return instantiated heater object linked to this controller"""
        return ControllerReader(name, self, RHEAT, unitstring, formatstring)

    def Tchannel_device(self, name='Tchannel'):
        """Return instantiated tchannel object for current controller"""
        return ControllerChannel(name, self)

    "==================== Device Methods ======================="

    def set_temperature_setpoint(self, temp_setpoint):
        """
        Set temperature setpoint
        """
        self.set_value(SET, temp_setpoint)
        if self.pd_device_index() == 2:  # Cryostream
            n = 0
            # Read Target Temperature
            while abs(float(self.get_value(RHEAT)) - temp_setpoint) > 0.01 and n < 20:
                sleep(0.5)
                self.set_value(RAMP, True)  # press Ramp button
                n += 1

    def ramp(self, rate=None):
        """
        ramp(): prints the status of the ramp
        ramp(5): set ramp ON at 5 K/min
        ramp(0): set ramp OFF
        """
        current_rate = self.get_value(RATE)
        current_ramp = self.get_value(RAMP)
        if rate is None:
            print('ramp: %s, ramp rate: %s' % (current_ramp, current_rate))
            return

        if rate > 0:
            self.set_value(RATE, str(rate))
            sleep(0.5)
            self.set_value(RAMP, '1')
            #cmdstr = 'RAMP 1, 1, '+str(rate)
            #caput(self.pvstring+'ASYN.AOUT',cmdstr)
            print('Setting ramp ON: %s K/min' % rate)
        else:
            self.set_value(RAMP, '0')
            #caput(self.pvstring+'ASYN.AOUT','RAMP 1, 0')
            print('Setting ramp OFF')
    set_ramp = ramp

    def heater(self, hrange=None):
        """
        Set heater range or get heater power %
            tcontrol.set_heater(): return current heater %
            tcontrol.set_heater('High'): set heater to full power on lakeshore 340
            tcontrol.set_heater(-1): set heater to full power on any device
            tcontrol.set_heater(0): turn off heater on any device
        """
        if hrange is None:
            return float(self.get_value(RHEAT))
        try:
            hrange = self.pvs[HEAT_OPT][hrange]
        except TypeError:
            pass
        except IndexError:
            hrange = self.pvs[HEAT_OPT][-1]
        self.set_value(HEAT, str(hrange))
        print('heater range set: %s' % hrange)
    set_heater = hrange = heater

    def warmup(self):
        """
        Sets the heating power to maximum, removes ramp and sets temperature to 300K
        """
        print('Warming up')
        self.heater(-1)
        self.ramp(0)
        self._tset_device(300)

    def control_chan(self, channel=None):
        """
        Sets the control channel of the Lakeshore cryostats
            tcontrol.control_chan()  # returns the current control channel
            tcontrol.control_chan(channel_string) sets control channel ('A', 'B', 'C' or 'D')
            tcontrol.control_chan(1)  # Control channel 1 (Any Lakeshore - Ta)
            tcontrol.control_chan(2)  # Control channel 2 (Any Lakeshore - Tb)
        """
        if channel is None:
            if self.pd_device_index() == 2:
                return 'Ta'
            return self.get_value(CHAN)
        try:
            channel = self.pvs[CH_OPT][channel]
        except TypeError:
            pass
        self.set_value(CHAN, str(channel))
        sleep(1)
        print('Control channel: %s' % self.control_chan())

    def pid(self, new_pid=None, p=None, i=None, d=None):
        """
        Sets or gets the current PID values
            tcontrol.pid()  # returns the current [P,I,D] values
            tcontrol.pid([P,I,D])  # Sets the P, I, D values
            tcontrol.pid(p=P, i=I, d=D)  # Sets the P, I, D values
        """
        if new_pid is None and p is None and i is None and d is None:
            P_pv = self.pvs[RP] % 'P'
            I_pv = self.pvs[RP] % 'I'
            D_pv = self.pvs[RP] % 'D'
            return [caget(P_pv), caget(I_pv), caget(D_pv)]
        try:
            p, i, d = new_pid
        except TypeError:
            pass
        if p is not None:
            P_pv = self.pvs[PID] % 'P'
            caput(P_pv, p)
            sleep(1)
        if i is not None:
            I_pv = self.pvs[PID] % 'I'
            caput(I_pv, i)
            sleep(1)
        if d is not None:
            D_pv = self.pvs[PID] % 'D'
            caput(D_pv, d)
            sleep(1)
        print('PID is %s' % self.pid())


class ControllerReader(ScannableMotionBase):
    """
    Device to read current temperature
    """
    def __init__(self, name, controller, sensor_label=RTA, unitstring='K', formatstring='%5.2f'):
        self.setName(name)
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(5)

        self.controller = controller
        self.sensor = sensor_label
        self.__doc__ += ' Current device: %s\n' % name

    def getPosition(self):
        return float(self.controller.get_value(self.sensor))

    def isBusy(self):
        return 0


class ControllerChannel(ScannableMotionBase):
    """
    Device to set and get temperature controller channel
    """
    def __init__(self, name, controller, formatstring='%s'):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat([formatstring])
        self.setLevel(5)

        self.controller = controller

    def getPosition(self):
        return self.controller.control_chan()

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, channel):
        self.controller.control_chan(channel)


class ControllerSetter(ScannableMotionBase):
    """
    Device to set temperature set point

      pos tcontrol 'lakeshore340'
      pos tset 20

    will return as soon as the controller has set the temperature.
    See help(tcontrol) for more information and how to use extra methods.

    Methods:
        tset.hrange(value): heater range: 0=OFF, -1=Max
	    tset.heater(): read only of the power of the heater
	    tset.control_chan(channel_string) sets control channel (1-4), ('A', 'B', 'C' or 'D')
	    tset.pid(): read PID values
	    tset.pid([P,I,D]): set PID values
	    tset.ramp(): prints the status of the ramp
        tset.ramp(5): set ramp ON at 5 K/min
        tset.ramp(0): set ramp OFF
        test.warmup(): Sets ramp OFF, setpoints=300K
    """
    def __init__(self, name, controller, unitstring='K', formatstring='%5.2f'):
        self.setName(name)
        self.setInputNames(['Tset'])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(5)

        self.controller = controller

        # Recover previous functionality
        self.hrange = self.heater = self.controller.heater
        self.control_chan = self.controller.control_chan
        self.pid = self.controller.pid
        self.ramp = self.controller.ramp
        self.warmup = self.controller.warmup

    def getPosition(self):
        return float(self.controller.get_value(SET))

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, new_temperature):
        self.controller.set_temperature_setpoint(new_temperature)


class TemperatureWaiter(ScannableMotionBase):
    """
    Device to set temperature set point and wait until temperature reached

    Usage:
      pos tcontrol 340
      pos twait [temperature, tolerance [, max_wait]]
      setpoint, current_temp = twait()

    will return when Ta is within *tolerance* of *temperature*,
    or will return after *max_wait* (if *max_wait* is not given, uses default).

    See help(tcontrol) for more information and how to use extra methods.

    Methods:
      twait.set_temperature_check_rate(seconds)  # Set the rate at which the temperature is checked, in seconds
      twait.set_proximity_temperature(temp)  # Set the temperature difference where the stabilisation wait will start
      twait.set_stabilisation_time(seconds)  # Set the stabilisation time after reaching the setpoint, in seconds
      twait.set_default_tolerance(temp)  # Set the default temperature difference where wait ends
      twait.set_default_max_wait(seconds)  # Set the default maximum time to wait for stabilisation, in seconds
      twait.stop()  # stops the loop at the next iteration
    """
    def __init__(self, name, setter, reader):
        """
        Instatiation parameters:
        :param name: str name
        :param setter: scannable Temperature setter (tset)
        :param reader: scannable Temperature reader (Ta)
        """
        self.setter = setter
        self.reader = reader

        self.setName(name)
        self.setInputNames([setter.name, 'tolerance'])
        self.setExtraNames([reader.name])
        self.Units = ['K']
        self.setOutputFormat(['%5.2f', '%5.2f', '%5.2f'])
        self.setLevel(5)

        self.temperature_setpoint = 0  # K
        self.temperature_tolerance = 0.5  # K
        self.max_wait = 1800.  # s
        self.temperature_check_rate = 30  # s
        self.proximity_temperature = 30  # K
        self.stabilisation_time = 10  # s
        self.default_tolerance = 0.5  # K
        self.default_max_wait = 1800.  # s
        self.stop_loop = False

    def stop(self):
        """Stops the wait loop on the next iteration"""
        self.stop_loop = True
        print('Stoping Twait... you may need to wait %1.0fs' % self.temperature_check_rate)

    def set_temperature_check_rate(self, check_rate_seconds=None):
        """Set the rate at which the temperature is checked, in seconds"""
        if check_rate_seconds is None:
            return self.temperature_check_rate
        self.temperature_check_rate = check_rate_seconds

    def set_proximity_temperature(self, temperature_difference=None):
        """Set the temperature difference where the stabilisation wait will start"""
        if temperature_difference is None:
            return self.proximity_temperature
        self.proximity_temperature = temperature_difference

    def set_stabilisation_time(self, stabilisation_time_seconds=None):
        """Set the stabilisation time after reaching the setpoint, in seconds"""
        if stabilisation_time_seconds is None:
            return self.stabilisation_time
        self.stabilisation_time = stabilisation_time_seconds

    def set_default_tolerance(self, temperature_tolerance=None):
        """Set the default temperature difference where wait ends"""
        if temperature_tolerance is None:
            return self.default_tolerance
        self.default_tolerance = temperature_tolerance

    def set_default_max_wait(self, max_wait_seconds=None):
        """Set the default maximum time to wait for stabilisation, in seconds"""
        if max_wait_seconds is None:
            return self.default_max_wait
        self.default_max_wait = max_wait_seconds

    def getPosition(self):
        return self.setter.getPosition(), self.temperature_tolerance, self.reader.getPosition()

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, temp_tol_max):
        temp_tol_max = dnp.asarray(temp_tol_max).reshape(-1)
        self.temperature_setpoint = temp_tol_max[0]
        self.temperature_tolerance = self.default_tolerance
        self.max_wait = self.default_max_wait
        if len(temp_tol_max) > 1:
            self.temperature_tolerance = temp_tol_max[1]
        if len(temp_tol_max) > 2:
            self.max_wait = temp_tol_max[2]
        if self.max_wait < 0:
            self.max_wait = 1e6

        self.setter.asynchronousMoveTo(self.temperature_setpoint)
        setpoint, tol, temp = self.getPosition()
        self.stop_loop = False
        # Initial loop - wait to get to temperature proximity
        while abs(temp - self.temperature_setpoint) > self.proximity_temperature and not self.stop_loop:
            print('*Waiting for temperature %.2f K to reach %.2f K +/- %.2f K, use twait.stop() to stop' % (temp, setpoint, self.temperature_tolerance))
            sleep(self.temperature_check_rate)
            setpoint, tol, temp = self.getPosition()

        nwaits = 0
        max_waits = self.max_wait // self.temperature_check_rate
        while abs(temp - self.temperature_setpoint) > self.temperature_tolerance and nwaits < max_waits and not self.stop_loop:
            print(' Waiting for temperature %.2f K to reach %.2f K +/- %.2f K, use twait.stop() to stop' % (temp, setpoint, self.temperature_tolerance))
            sleep(self.temperature_check_rate)
            setpoint, tol, temp = self.getPosition()
            nwaits += 1
        if self.stop_loop:
            print(' twait stopped at %.2f K' % temp)
        else:
            print(' Stabilising at %.2f K' % temp)
            sleep(self.stabilisation_time)
        setpoint, tol, temp = self.getPosition()
        if abs(temp - self.temperature_setpoint) > self.temperature_tolerance:
            print(' Temperature %.2f K is outside %.2f K +/- %.2f K' % (temp, setpoint, self.temperature_tolerance))


"""
tcontrol = TemperatureController('tcontrol')
tset = tcontrol.tset_device('tset')
Ta = tcontrol.Ta_device()
Tb = tcontrol.Tb_device()
Tsample = tcontrol.Tsample_device()
twait = tcontrol.twait_device('twait', new_tset, new_tsample)
"""
