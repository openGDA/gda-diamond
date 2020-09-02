'''
define class to control EPICS Femto Beckhoff ADC start and stop, The ADC data are actually collected into bin point waveform.

@author: Fajin Yuan
@organization: Diamond Light Source Ltd
@since 04 August 2020 
'''

from gda.epics import CAClient
from scannable.waveform_channel.WaveformChannelPollingInputStream import WaveformChannelPollingInputStream
from org.slf4j import LoggerFactory
from threading import Timer
import installation
from dataGenerator.CounterTimer import countTimer
from dataGenerator.waveformDataGenerator import WaveformDataGenerator
from scisoftpy.jython.jyrandom import randint

TIMEOUT = 5
ADC_SAMPLING_RATE=1000.0
    
class ADCWaveformChannelController(object):
    # e.g. adc_root_pv = BL21I-EA-SMPL-01:ADC_ACQ_GRP:

    def __init__(self, name, adc_root_pv):
        self.logger = LoggerFactory.getLogger("ADCWaveformChannelController:%s" % name)
        self.verbose = False
        self.name = name
        #EPICS PVs control 3 ADCs: ADC_ACQ_GRP 
        self.adc_root_pv = adc_root_pv
        self.pv_reset = CAClient(adc_root_pv + 'RESET.PROC')
        self.pv_disa = CAClient(adc_root_pv + 'DISA')
        self.pv_average= CAClient(adc_root_pv + 'AVERAGE')
        self.pv_samples= CAClient(adc_root_pv + 'SAMPLES')
        self.pv_required_capture_number = CAClient(adc_root_pv + 'REQ_CAPS')
        self.pv_trigger_start = CAClient(adc_root_pv + 'TRIGGER.PROC')

        self.configure()
        self.exposure_time = 1
        self.exposure_time_offset=.0
        self.number_of_positions = 0
        self.started = False
        self.hardware_trigger_provider=None
        self.stream=None
        #state variables to ensure method of this object is only called once as EPICS is doing the fan-out to 3 ADCs
        self.erase_start_called = False
        self.stop_called = False
        
    def set_hardware_trigger_provider(self, hardwareTriggerProvider):
        self.hardware_trigger_provider=hardwareTriggerProvider
    
    def get_hardware_trigger_provider(self):
        return self.hardware_trigger_provider
    
    def configure(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'configure()...'))
        if installation.isLive():
            self.pv_disa.configure()
            self.pv_samples.configure()
            self.pv_average.configure()
            self.pv_required_capture_number.configure()
            self.pv_reset.configure()
            self.pv_trigger_start.configure()
        else:
            if self.verbose: self.logger.info("configure '%s' for dummy operation...')" % (countTimer.getName()))
            
    def erase(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase()...'))
        self.started = False
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase()'))

    def erase_and_start(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'erase_and_start()...'))
        if installation.isLive() and not self.erase_start_called:
            self.erase_start_called = True
            self.pv_reset.caput(1)
            self.pv_disa.caput(0)  # enable the ADC detectors
            samples = round(self.exposure_time * ADC_SAMPLING_RATE)
            self.pv_average.caput(samples)
            self.pv_samples.caput(samples)
            self.pv_required_capture_number.caput(self.number_of_positions) # Set the total number of points to be captured time
            self.pv_trigger_start.caput(TIMEOUT, 1)
        else:
            #ADC hardwares are not used in Dummy mode
            pass
        # delayed starting capture counts into waveform buffer to give time for ID and PGM motions to accelerate to required velocity
        started_timer = Timer(1.5, self._delayed_start_complete) # Failed at 0.5s, Ok at 1.5s.
        started_timer.start()
        if self.verbose: self.logger.info("%s %s" % (self.name,'...erase_and_start()'))

    def _delayed_start_complete(self):
        self.started = True
        if self.verbose: self.logger.info("%s %s" % (self.name,'..._delayed_start_complete()'))

    def stop(self):
        if self.verbose: self.logger.info("%s %s" % (self.name,'stop()...'))
        if installation.isLive() and not self.stop_called:
            self.stop_called = True
            self.pv_disa.caput(1)
        else:
            #ADC Hardwares are not available in Dummy mode
            pass
        if self.stream:
            self.stream.stop() # stop waveform polling stream.
        self.started = False
        if self.verbose: self.logger.info("%s %s" % (self.name,'...stop()'))
    
    # Provide functions to configure WaveformChannelScannable

    def getChannelInputStream(self, channel_pv_suffix):
        # Channels numbered from 1
        self.stream = WaveformChannelPollingInputStream(self, channel_pv_suffix)
        # The NORD Epics pv cannot be listened to, hence the polling
        self.stream.verbose = self.verbose
        return self.stream

    def getChannelInputStreamFormat(self):
        return '%f'

    # Provide functions to configure WaveformChannelPollingInputStream

    def getChannelInputStreamType(self):
        return float

    def getChannelInputStreamCAClients(self, channel_pv_prefix):
        if installation.isLive():
            pv_waveform = CAClient(channel_pv_prefix + 'BINPOINT')
            pv_count =    CAClient(channel_pv_prefix + 'BINPOINT:NLAST.B')
        else:
            waveform=WaveformDataGenerator()
            waveform.useGaussian=True
            if waveform.useGaussian and waveform.gaussian is None:
                waveform.initializeGaussian()
            waveform.data=[]
            waveform.channel=randint(3,9)
            pv_waveform = waveform
            pv_count=self.number_of_positions
        return pv_waveform, pv_count

    def getExposureTime(self):
        return self.exposure_time

    def getChannelInputStreamAcquiring(self):
        return self.started
