# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from gda.device.scannable import PositionInputStream
import java.util.Vector
import time

# TODO: This should be moved to mt-config and the requirements for both i16
# and i10 should be combined.

class WaveformChannelPollingInputStream(PositionInputStream):

    def __init__(self, controller, channel):
        self.pv_waveform, self.pv_count = controller.getChannelInputStreamCAClients(channel)
        self.elements_read = 0 # none available
        self.type = controller.getChannelInputStreamType()
        self.configure()
        self.reset()

    def configure(self):
        self.pv_waveform.configure()
        self.pv_count.configure()

    def reset(self):
        # count should read 0 after an erase, but will not actually be reset
        # until an erase & start.        
        self.elements_read = -1

    # Implement the PositionInputStream:read

    def read(self, max_to_read_in_one_go):
        if self.elements_read == -1:
            self.elements_read = 0
            ##return java.util.Vector([0])
        new_available = self._waitForNewElements()
        all_data = self.pv_waveform.cagetArrayDouble(self.elements_read + new_available)
        new_data = all_data[self.elements_read:self.elements_read + new_available]
        self.elements_read += new_available
        return java.util.Vector([self.type(el) for el in new_data])

    def _waitForNewElements(self):
        """return the number of new elements available, polling until some are"""
        
        while True:
            elements_available = int(float(self.pv_count.caget()))
            if elements_available > self.elements_read:
                return elements_available - self.elements_read
            time.sleep(.2)
