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
        self.hardwareTriggerProvider=None
        self.startTimeSet = False

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
        self.startTimeSet = False
        self.stoppedExplicitly = False # see I21-989
        
    def stop(self):
        #flag to stop polling loop
        self.stoppedExplicitly=True

    # Implement the PositionInputStream:read

    def read(self, max_to_read_in_one_go):
        if self.verbose: self.logger.info('read(%r)...  elements_read=%r' % (max_to_read_in_one_go, self.elements_read))
        if self.hardwareTriggerProvider is None:
            self.hardwareTriggerProvider=self._controller.getHardwareTriggerProvider()
        if installation.isLive():
            new_available = self._waitForNewElements()
            all_data = self.pv_waveform.cagetArrayDouble(self.elements_read + new_available)
        else:
            if self.hardwareTriggerProvider._start_time is not None and not self.startTimeSet:
                self.start_time = time.time()
                self.startTimeSet=True
            new_available = self._waitForNewElements()
            if self.channel in ['GRT:PITCH:','MIR:PITCH:','PGM:ENERGY:']:
                if self.channel == 'GRT:PITCH:':
#                     print "%s waveform is %r" % (self.channel, self.hardwareTriggerProvider.grating_pitch_positions)
                    all_data=self.hardwareTriggerProvider.grating_pitch_positions[:self.elements_read + new_available]
                elif self.channel == 'MIR:PITCH:':
#                     print "%s waveform is %r" % (self.channel, self.hardwareTriggerProvider.mirror_pitch_positions)
                    all_data=self.hardwareTriggerProvider.mirror_pitch_positions[:self.elements_read + new_available]
                elif self.channel == 'PGM:ENERGY:':
#                     print "%s waveform is %r" % (self.channel, self.hardwareTriggerProvider.pgm_energy_positions)
                    all_data=self.hardwareTriggerProvider.pgm_energy_positions[:self.elements_read + new_available]
            else:
                all_data = self.pv_waveform.generateData(self.channel, self.elements_read + new_available)
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
        new_element_timeout = exposure_time + 20.0 
        
        while True and not self.stoppedExplicitly:
            if installation.isLive():
                elements_available = int(float(self.pv_count.caget()))
                from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
                if isinstance(self._controller, BinpointWaveformChannelController):   
                    elements_available = elements_available + 1 #BINPOINT:NLAST.B index starts at 0, -1 is waveform empty
            else:
                self.logger.info("DUMMY mode: number of positions set in WaveformChannelScannable to its controller is %r" % self._controller.number_of_positions)
                #the following line does not ensure cvscan complete 100%
                #elements_available = sum(x<=float(self.hardwareTriggerProvider._pgm_grat_pitch.getPosition()/1000.0) for x in self.hardwareTriggerProvider.grating_pitch_positions)
                if not self.startTimeSet:
                    elements_available = int(self._controller.number_of_positions)
                else:
                    elapsedTime = time.time() - self.start_time
                    if elapsedTime < self._controller.getHardwareTriggerProvider().getTotalTime():
                        elements_available = int(self._controller.number_of_positions * elapsedTime/self._controller.getHardwareTriggerProvider().getTotalTime())
                    else:
                        elements_available = int(self._controller.number_of_positions)

            #print "self.elements_read = %d" % self.elements_read
            #print "element_available = %d" % elements_available
            # check continuous move started then poll the data so far
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
                if elements_available == self.elements_read and self.elements_read == self._controller.number_of_positions:
                    self.logger.info('_waitForNewElements() elements_available=%r, elements_read=%r, number_of_positions_expected=%r, Data collection should finish now!' % (
                                    elements_available,  self.elements_read, self._controller.number_of_positions))
                    self.stop() #all elements are already read, so this thread can stop
            time.sleep(sleep_time)
