# scannable.xpsdatagathering

from gda.device.scannable import ScannableBase
from gda.device.detector.areadetector.v17.ADDriverPilatus import Gain
from gdascripts.scannable.epics.PvManager import PvManager
from gda.epics import LazyPVFactory
from gda.jython import InterfaceProvider
import time
import java.lang.Boolean
import java.util.function.Predicate
from gda.jython import InterfaceProvider
import os


TIMEOUT = 10

ENABLE_AXES_TO_ACQUIRE = False

DEBUG = False


def _get_current_scan_number():
    scanInfo = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
    return int(scanInfo.getScanNumber())


def _get_datadir():
    return InterfaceProvider.getPathConstructor().createFromDefaultProperty()


class IsFalsePredicate(java.util.function.Predicate):
    
    def apply(self, o):
        return not o


class ScannableXPSDataGatherer(ScannableBase):
    
    def __init__(self, name, pvroot='BL16I-CS-IOC-15:XPSG:'):
        self.name = name
        self.inputNames = ['rate', 'delay_time', 'total_time']
        self.extraNames = ['file_number']
        self.outputFormat = ['%.5f', '%.5f', '%.5f', '%i']
        self.level = 4

        self.pvs = PvManager(pvroot=pvroot)
        self.pv_startacquire = LazyPVFactory.newNoCallbackBooleanFromShortPV(pvroot + 'START-ACQUIRE')
        self.pv_aquiring = LazyPVFactory.newNoCallbackBooleanFromShortPV(pvroot + 'ACQUIRING')
        
        self._rate_and_time_set_for_this_scan = False
        self._last_delay_time = -999
        self._next_file_number = -999
        

    def atScanStart(self):
        self._rate_and_time_set_for_this_scan = False
        if ENABLE_AXES_TO_ACQUIRE:
            for axis in 1, 2, 3, 4, 5 ,6:
                self.pvs['AXIS-ENABLE-0' + str(axis)].caput(TIMEOUT, True)
        self._set_dirname_and_create_directory()
        self.pvs['COUNTER'].caput(TIMEOUT, 0)
        self.pvs['FILENAME'].caput(TIMEOUT, "")

    def _set_dirname_and_create_directory(self):
        dirname = os.path.join(_get_datadir(), '%i-xps' % _get_current_scan_number())
        if len(dirname) > 39:
            raise Exception("Path exceeded 39 characters (%i): %s" % (len(dirname), dirname))
        self.pvs['DIRNAME'].caput(TIMEOUT, dirname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        print self.name + " writing to: " + dirname
        

    def asynchronousMoveTo(self, target):
        rate, delay_time, total_time = [float(element) for element in tuple(target)]
        self._last_delay_time = delay_time
        if not self._rate_and_time_set_for_this_scan:
            self.pvs['CAPTURE-HERTZ'].caput(TIMEOUT, rate)
            self.pvs['CAPTURE-TIME'].caput(TIMEOUT, total_time)
            self._rate_and_time_set_for_this_scan = True
        if DEBUG:
            print "*** start acquire"
        if self.pv_startacquire.get():
            raise Exception(self.name + " is already acquiring.")
        self._next_file_number = self.pvs['COUNTER'].caget()
        self.pv_startacquire.putNoWait(True)
        time.sleep(delay_time)

    def waitWhileBusy(self):
        return  # The thing waited for delay_time during asynchronousMoveTo()

    def isBusy(self):
        return False  # The thing waited for delay_time during asynchronousMoveTo()

    def getPosition(self):
        rate = self.pvs['CAPTURE-HERTZ'].caget()
        total_time = self.pvs['CAPTURE-TIME'].caget()
        return rate, self._last_delay_time, total_time, self._next_file_number

    def atPointEnd(self):
        self.pv_startacquire.setValueMonitoring(True)
        if DEBUG:
            print "*** start waiting"
        self.pv_startacquire.waitForValue(IsFalsePredicate(), 3600)
        if DEBUG:
            print "*** stop waiting"

    def stop(self):
        self.pvs['STOP-ACQUIRE'].caput(True)
        self._cleanup()
    
    def atScanEnd(self):
        self._cleanup()

    def atCommandFailure(self):
        self.pvs['STOP-ACQUIRE'].caput(True)
        self._cleanup()
    
    def _cleanup(self):
        self.pv_startacquire.setValueMonitoring(False)