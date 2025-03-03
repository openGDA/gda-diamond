'''
Please see I07-601 JIRA ticket for details of this scannable'd design.

Created on 10 Feb 2025

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from uk.ac.gda.api.io import PathConstructor
from time import sleep
from gdascripts import installation

class IviumMethodScannableClass(ScannableMotionBase):
    '''
    A Scannable class that supports Ivium device to collect data in 'Method' mode using IviumSoft.
    '''

    def __init__(self, name, pv_root, channel_number, subdir = 'processing'):
        '''
        Constructor
        '''
        self.setName(name)
        self.setExtraNames([name])
        self.setInputNames([])
        self.setOutputFormat(["%s"])
        self.pv_root = pv_root
        self.ch_number =  channel_number
        self.data_file_name = None
        self.subdir = subdir
        self._busy = False
        self.ch_status = CAClient(pv_root + "CHAN" + str(channel_number) + ":DeviceStatus_RBV")
        self.ch_start = CAClient(pv_root + ":PORT" + str(channel_number) + ":StartMethod")
        self.ch_stop = CAClient(pv_root + "PORT" + str(channel_number) + ":StopMethod")

    def configure(self):
        if self.isConfigured():
            return
        if installation.isLive():
            if not self.ch_start.isConfigured():
                self.ch_start.configure()
            if not self.ch_status.isConfigured():
                self.ch_status.configure()
            if not self.ch_stop.isConfigured():
                self.ch_stop.configure()
        self.setConfigured(True)

    def set_data_file_name(self, fname):
        self.data_file_name = fname

    def get_data_file_name(self):
        return self.data_file_name

    def getPosition(self):
        path = PathConstructor.createFromDefaultProperty()
        if self.subdir:
            return path + "/" + self.subdir + "/" + self.data_file_name
        else:
            return path + "/" + self.data_file_name

    def asynchronousMoveTo(self, newpos):  # @UnusedVariable
        self.configure()
        if self.data_file_name is None:
            raise ValueError("Data file name is None. Please set data file name before using %s", self.getName())
        self._busy = True
        if installation.isLive():
            self.ch_start.caput(1)
        else:
            print("dummy mode: start method called")
        sleep(0.1) # give time for EPICS to respond
        self._busy = False

    def isBusy(self):
        if installation.isLive():
            status = self.ch_status.caget()
            return self._busy or status != 2
        else:
            return False

    def stop(self):
        if installation.isLive():
            self.ch_stop.caput(1)
        self._busy = False
