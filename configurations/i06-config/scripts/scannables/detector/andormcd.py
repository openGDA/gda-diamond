'''
Created on 23 Jan 2014

@author: mew09119
'''
from gda.device.detector import DetectorBase
from gda.epics import LazyPVFactory
import time
from gda.jython import InterfaceProvider
from gda.data import PathConstructor
import os.path
import os
from gda.scan import ScanBase

#scan motor 1 10 1 andormcd 1


DEBUG = True
PARAMETER_FILES_PATH = "/dls/i06-1/var/andorConfig/"

class AndorMCD(DetectorBase):

    def __init__(self, name, triggerpv='BL06J-EA-USER-01:AO1', busypv='BL06J-EA-USER-01:AI1'):
        self.name = name
        self.inputNames = []
        self.extraNames = [name + '_collectiontime', name + '_filepath']
        self.outputFormat = ['%.3f', '%s']

        self._triggerpv = LazyPVFactory.newDoublePV(triggerpv)
        self._busypv = LazyPVFactory.newDoublePV(busypv)
        self._next_image_number = 0

        self.nb_frames = 1
        self.background = True

    def prepareForCollection(self):
        self._next_image_number = 1
        self.scannumber = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation().getScanNumber()
        
        # Create folder for scannumber '12345-' + name + '-files'
        self._write_commands_file(self.getCollectionTime())
        self._write_background_file(self.background)
        self._write_saveinfo_file()
        
        target_dir = self._get_target_directory()
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        time.sleep(5)
        # set collection time from self.getCollectionTime

    def collectData(self):
        self._send_hardware_trigger()
        self._next_image_number += 1

#     def waitWhileBusy(self):
#         while self.isBusy():
#             ScanBase.checkForInterrupts()
#             time.sleep(.1)
#         time.sleep(1)

    def isBusy(self):
        return bool(self._busypv.get() > 1.)  # On is about 3v

    def _get_target_directory(self):
        datadir = PathConstructor.createFromDefaultProperty()
        return os.path.join(datadir, '%05i-%s-files' % (self.scannumber, self.name)) 

    def readout(self):
        pathname = os.path.join(self._get_target_directory(), '%i.sif' % self._next_image_number)
        return self.getCollectionTime(), pathname

    def _write_commands_file(self, collection_time):
        if DEBUG:
            print "writing command file for collection time:", collection_time
        commands = ["stim %.3f" % collection_time, "snsi %d" % self.nb_frames, "getm", "gtim", "gnsi"]
        commandfilepath = os.path.join( PARAMETER_FILES_PATH, "commands.txt" )
        commandsfile = open( commandfilepath, mode = 'w' )
        for command in commands:
            commandsfile.write(command + "\r\n") #windows line terminator
        commandsfile.close()

    def _write_saveinfo_file(self):
        if DEBUG:
            print "writing saveinfo file for directory:", self._get_target_directory()
        saveinfofilepath = os.path.join(PARAMETER_FILES_PATH, "saveinfo.txt")
        saveinfofile = open(saveinfofilepath, mode='w')
        paths = "Z:" + PathConstructor.createFromDefaultProperty()[10:]
        savepath = os.path.join( paths, "%05i-%s-files" % (self.scannumber, self.name) )
        saveinfofile.write( savepath + "/\r\n%05d" % self._next_image_number )
        saveinfofile.close()

    def _write_background_file(self, background):
        if DEBUG:
            print "writing background switch file"
        backgroundswitchpath = os.path.join(PARAMETER_FILES_PATH, "background.txt")
        backgroundfile = open(backgroundswitchpath, mode='w')
        backgroundfile.write('1' if background else '0')
        backgroundfile.close()

    def _send_hardware_trigger(self):
        self._triggerpv.putWait(10.) # Voltage divider in connector drops this to 5v
        clock_start = time.clock()
        # Waiting up to two seconds for response that exposure has started:
        while not self.isBusy():
            if (time.clock() > clock_start + 2):
                raise Exception("Andor MCD did not indicate across Epics that it was exposing within 2s timeout")
            time.sleep(.01)
        self._triggerpv.putWait(0.)
