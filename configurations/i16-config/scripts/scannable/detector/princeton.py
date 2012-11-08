from gda.device.detector import DetectorBase
import subprocess
from time import sleep
import string
from gda.jython.commands.InputCommands import requestInput as raw_input

def hexavigesimal(n):
    if n < 0:
        raise ValueError('value must be non-negative')
    h = []
    while True:
        n, r = divmod(n, 26)
        h[0:0] = string.letters[r]
        if n == 0:
            return ''.join(h)

class PrincetonDetector(DetectorBase):
    
    def __init__(self, name, trigger_scannable, readout_time=2, filename_fmt='/dls/i16/data/2012/mt7277-1/ccddata/test%i.TIF'): # 1.90s according to software

        self.name = name
        self.trigger_scannable = trigger_scannable
        self.readout_time = readout_time
        self.filename_fmt = filename_fmt
        self.file_number = 0
        
        self.inputNames = []
        self.extraNames = ['path']#'acquire_time', 'image', 'path'] 
        self.level = 9
        self.outputFormat = ['%.2f'] # '%i', '%s']
        self.image_number = -1
        
        
    def createsOwnFiles(self):
        return True
    
    @property
    def multi_image_filepath(self):
        return self.filename_fmt % self.file_number
      
    @property
    def filepath(self):
        return self._single_image_filepath(self.image_number)
     
    def _single_image_filepath(self, image_number):
        b26 = hexavigesimal(image_number).rjust(3, 'a')
        left = self.multi_image_filepath.split('.')[0]
        return left + b26 + '.tif'

    def _prompt_for_file_number(self, default):
        s = raw_input('Princeton image number [default:%i]' % default)
        if s == '':
            return default
        return int(s)

    def atScanStart(self):
        self.file_number += 1
        self.file_number = self._prompt_for_file_number(self.file_number)
        
        print '*** ', self.name, " expecting images in file : ", self.multi_image_filepath
        self.image_number = -1

    def collectData(self):
        self.image_number += 1
        print '*** ', self.name, "collecting image :", self.image_number
        self.trigger_scannable.asynchronousMoveTo(self.getCollectionTime() + self.readout_time)

    def isBusy(self):
        return self.trigger_scannable.isBusy()
        
    def waitWhileBusy(self):
        return self.trigger_scannable.waitWhileBusy()
                        
    def readout(self):
        return self.filepath
        
    def atScanEnd(self):
        self._tiffsplit(self.multi_image_filepath)
    
    def _tiffsplit(self, filepath):
        prefix = ''.join(filepath.split('.')[:-1])
        print "*** Waiting 5 seconds for file to cross Lustre"
        sleep(5)
        args = ['tiffsplit', filepath, prefix]
        print '*** ', args
        result = subprocess.check_call(args)
        if result != 0:
            raise Exception("Problem splitting tif file '%s' : %s" % (filepath, result))
        print '*** tiffsplit complete'
