from gda.observable import IObserver
from gda.device import TemperatureStatus

import logging
logger = logging.getLogger('i11.csb_monitor')

TRACE = 5

class CsbPidMonitor(IObserver):
    def __init__(self, csb, upper, lower, high_p, low_p):
        self._csb = csb
        self._upper = upper
        self._lower = lower
        self._high = high_p
        self._low = low_p
        self._last = csb.currentTemperature

    def update(self, src, evt):
        if isinstance(evt, TemperatureStatus):
            temp = evt.currentTemperature
            logger.log(TRACE, "Update (%f) received from %s", temp, src.name)
            logger.log(TRACE, 'last: %f, current: %f, lower: %f, upper: %f', self._last, temp, self._lower, self._upper)
            if self._last <= self._upper < temp:
                # temp gone above threshold
                self._run(self._high)
            elif temp <= self._lower < self._last:
                # temp gone below threshold
                self._run(self._low)
            self._last = temp

    def _run(self, p):
        logger.info("Changing %s to P=%f", self._csb.name, p)
        self._csb.controller.proportional = p


