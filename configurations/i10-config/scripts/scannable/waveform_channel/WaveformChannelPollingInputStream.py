# Based on gda-mt.git/configurations/i16-config/scripts/scannable/scaler.py

from datetime import datetime, timedelta
from gda.device.scannable import PositionInputStream
import java.util.Vector
from java.util import NoSuchElementException
from org.slf4j import LoggerFactory
import time
import installation

class WaveformChannelPollingInputStream(PositionInputStream):

    def __init__(self, controller, channel):
        self.logger = LoggerFactory.getLogger("WaveformChannelPollingInputStream:%r:%r" % (controller.name, channel))
        self.verbose = False
        
        self._controller = controller
        self.channel=channel
        self.pv_waveform, self.pv_count = controller.getChannelInputStreamCAClients(channel)
        self.elements_read = 0 # none available
        self.type = controller.getChannelInputStreamType()
        self.configure()
        self.reset()
        self.stoppedExplicitly=False

    def configure(self):
        if installation.isLive():
            self.pv_waveform.configure()
            self.pv_count.configure()
        else:
            self.logger.info("DUMMY mode: pv_count at configure() is %r" % self.pv_count)


    def reset(self):
        if self.verbose: self.logger.info('reset()...')
        self.verbose = self._controller.verbose
        self.elements_read = 0
        
    def stop(self):
        self.stoppedExplicitly=True

    # Implement the PositionInputStream:read

    def read(self, max_to_read_in_one_go):
        if self.verbose: self.logger.info('read(%r)...  elements_read=%r' % (max_to_read_in_one_go, self.elements_read))
        #if self.elements_read == -1:
        #    self.elements_read = 0
        #    ##return java.util.Vector([0])
        new_available = self._waitForNewElements()
        if installation.isLive():
            all_data = self.pv_waveform.cagetArrayDouble(self.elements_read + new_available)
        else:
            if self.channel in ['GRT:PITCH:','MIR:PITCH:','PGM:ENERGY:']:
                all_data=self.pv_waveform[:self.elements_read + new_available]
            else:
                self.pv_waveform.pointCounter+=1
                if self.pv_waveform.useGaussian:
                    self.pv_waveform.resetGaussian()
                all_data = self.pv_waveform.generateData(new_available)
                self.logger.debug("DUMMY mode: generate %r elements" % (new_available))
        new_data = all_data[self.elements_read:self.elements_read + new_available]
        self.elements_read += new_available
        if self.verbose: self.logger.info('...read() all_data[0:6] = %r' % (all_data[0:6]))
        if self.verbose: self.logger.info('...read() (elements_read=%r) new data = %r' % (self.elements_read,
               java.util.Vector([self.type(el) for el in new_data])))
        return java.util.Vector([self.type(el) for el in new_data])

    def _waitForNewElements(self):
        """return the number of new elements available, polling until some are"""
        #if self.verbose: self.logger.info('_waitForNewElements()... elements_read=%r' % (self.elements_read))
        acquiring_old = self._controller.getChannelInputStreamAcquiring()
        exposure_time = self._controller.getExposureTime()
        sleep_time = exposure_time if exposure_time > 0.2 else 0.2
        log_timeout = exposure_time + 5
        log_time = last_element_time = datetime.now()
        new_element_timeout = exposure_time + 200 # it takes about 200 second to complete a full range move of pgm_grit_pitch.

        while True and not self.stoppedExplicitly:
            if installation.isLive():
                elements_available = int(float(self.pv_count.caget()))
            else:
                self.logger.info("DUMMY mode: number of positions set in WaveformChannelScannable to its controller is %r" % self._controller.number_of_positions)
                elements_available = int(self._controller.number_of_positions)

            #print "self.elements_read = %d" % self.elements_read
            #print "element_available = %d" % elements_available
            # Some waveform PVs keep returning old data for a short time even after a new acq is started and even retain the old count
            # for some time after the new acq has started, so check with the controller before trusting the count
            acquiring = self._controller.getChannelInputStreamAcquiring()
            if acquiring:
                if acquiring_old <> acquiring:
                    self.logger.info('_waitForNewElements() elements_available=%r, elements_read=%r, acquiring now %r, was %r' % (
                                    elements_available, self.elements_read, acquiring, acquiring_old))
                    acquiring_old = acquiring
                    last_element_time = log_time = datetime.now()
                if elements_available > self.elements_read:
                    last_element_time = log_time = datetime.now()
                    if self.verbose: self.logger.info('_waitForNewElements() elements_available=%r, elements_read=%r, acquiring %r, %r new_elements available' % (
                                                    elements_available,  self.elements_read, acquiring,
                           elements_available - self.elements_read))
                    return elements_available - self.elements_read
                elif (datetime.now() - last_element_time) > timedelta(seconds=new_element_timeout):
                    self.logger.error("_waitForNewElements() no new elements for  %r seconds, raising an exception..." % new_element_timeout)
                    raise NoSuchElementException("no new elements for  %r seconds" % new_element_timeout)
            if self.verbose and (datetime.now() - log_time) > timedelta(seconds=log_timeout):
                self.logger.info('_waitForNewElements() elements_available=%r, elements_read=%r, acquiring %r, no new elements for %r seconds!' % (
                                elements_available,  self.elements_read, acquiring, log_timeout))
                log_time = datetime.now()
            time.sleep(exposure_time)
