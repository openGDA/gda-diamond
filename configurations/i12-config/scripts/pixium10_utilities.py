from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos, scan 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
from gdascripts.parameters import beamline_parameters
from gda.factory import Finder


finder = Finder.getInstance()
try:
    pixium10_hdf=finder.find("pixium10_hdf")
    pixium10_tif=finder.find("pixium10_tif")
except:
    print "pixium10_hdf/pixium10_tif already defined"
    
    

def pixium10_changeExposure(exposure, waitsec=2):
    pixium10_hdf.stop()
    sleep(waitsec)
    pixium10_hdf.getAdditionalPluginList()[0].getNdFileHDF5().setLazyOpen(True)
    caput("BL12I-EA-DET-10:TIFF:LazyOpen", True)
    pixium10_hdf.setBaseExposure(exposure)
    pixium10_hdf.setBaseAcquirePeriod(exposure)
    pixium10_hdf.calibrate()
    pixium10_hdf.calibrate()
    msg = "\npixium10 exposure changed to %.4f s; detector calibrated with shortest possible acquire period of %.4f s. Shutter closed." %(pixium10_hdf.getBaseExposure(), pixium10_hdf.getBaseAcquirePeriod())
    print msg
alias("pixium10_changeExposure")


def pixium10_changeExposureAndAcquirePeriod(exposure, acquire, waitsec=2):
    pixium10_hdf.stop()
    sleep(waitsec)
    pixium10_hdf.getAdditionalPluginList()[0].getNdFileHDF5().setLazyOpen(True)
    caput("BL12I-EA-DET-10:TIFF:LazyOpen", True)
    pixium10_hdf.setBaseExposure(exposure)
    pixium10_hdf.setBaseAcquirePeriod(acquire)
    acqPeriod_before = pixium10_hdf.getBaseAcquirePeriod()
    pixium10_hdf.calibrate()
    pixium10_hdf.calibrate()
    acqPeriod_after = pixium10_hdf.getBaseAcquirePeriod()
    eps = 0.01
    if abs(acqPeriod_after-acquire)>eps:
        msg_wrn_ = "WARNING: the input acquire period of %.4f s is different from that set on the detector after calibration: %.4f s!" %(acqPeriod_before, acqPeriod_after)
        print msg_wrn
    msg = "pixium10 exposure changed to %.4f s and acquire period to %.4f s; detector calibrated. Shutter closed." %(pixium10_hdf.getBaseExposure(), pixium10_hdf.getBaseAcquirePeriod())
    print msg
alias("pixium10_changeExposureAndAcquirePeriod")


def pixium10_preview():
    caput("BL12I-EA-DET-10:CAM:Acquire", 0)         # 0 for OFF, 1 for ON
    sleep(2)
    caput("BL12I-EA-DET-10:CAM:MotionBlur", 0)      # 0 for OFF, 1 for ON
    caput("BL12I-EA-DET-10:CAM:NumExposures", 1)    # setting back to single exposure for preview
    caput("BL12I-EA-DET-10:CAM:ArrayCounter", 0)    # resetting counter to 0
    caput("BL12I-EA-DET-10:CAM:DataType", 3)    # 3 for UInt16, 5 for UInt32
    caput("BL12I-EA-DET-10:CAM:ImageMode", 2)   # 0 for SINGLE, 2 for CONTINUOUS
    sleep(0.1)
    caput("BL12I-EA-DET-10:CAM:Acquire", 1)     # 0 for OFF, 1 for ON
    print "pixium10_preview set"
alias("pixium10_preview")


from gda.epics import CAClient
from gda.device.scannable import PseudoDevice

class ExcludeEarlyFramesDefaultHandler(PseudoDevice):
    # constructor
    def __init__(self, name, pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%d"])
        self.pvvalue=int(pvvalue)
        self.pvname=pvname
        self.cli=CAClient(pvname)
        self.cli_exposures=CAClient("BL12I-EA-DET-10:CAM:NumExposures")
        self.backup_pos=None
        self.current_pos=None
        self.warning_printed=False
        
    def reset(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        if self.backup_pos is not None:
            self.cli.caput(self.backup_pos)
            self.current_pos=self.backup_pos
    
    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.current_pos

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position=False):
        print "rawAsynchronousMoveTo"
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        
        if new_position is not None:
            self.current_pos=int(new_position)
            self.cli.caput(self.cli.current_pos)
        return

    # Returns the status of this Scannable
#    def rawIsBusy(self):
#        #print "hello from rawIsBusy"
#        sleep(1)
#        return

    def isBusy(self):
        return False
    
    def atScanStart(self):
        print "atScanStart"
        self.warning_printed=False
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        #self.cli.caput(self.pvvalue)           # exclude early frames set to OFF

    def atPointStart(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        if not self.cli_exposures.isConfigured():
            self.cli_exposures.configure()
        exposures = int(self.cli_exposures.caget())
        if exposures > 1:
            if not self.warning_printed:
                print "WARNING: Forcing early frames to be excluded for this summing of %d exposures per image!" %(exposures)
                self.warning_printed=True
            self.cli.caput(1)
        else:
            self.cli.caput(self.pvvalue)
        #pass
        
    def atPointEnd(self):
        pass
    
    def stop(self):
        self.reset()
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()
    
#earlyFramesOFF=ExcludeEarlyFramesDefaultHandler('earlyFramesOFF', pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0)


class ExcludeEarlyFramesHandler(PseudoDevice):
    # constructor
    def __init__(self, name, pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%d"])
        self.pvvalue=int(pvvalue)
        self.pvname=pvname
        self.cli=CAClient(pvname)
        self.cli_exposures=CAClient("BL12I-EA-DET-10:CAM:NumExposures")
        self.backup_pos=None
        self.current_pos=None
        self.warning_printed=False
        
    def reset(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        if self.backup_pos is not None:
            self.cli.caput(self.backup_pos)
            self.current_pos=self.backup_pos
    
    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.current_pos

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position=False):
        print "rawAsynchronousMoveTo"
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        
        if new_position is not None:
            self.current_pos=int(new_position)
            self.cli.caput(self.cli.current_pos)
        return

    # Returns the status of this Scannable
#    def rawIsBusy(self):
#        #print "hello from rawIsBusy"
#        sleep(1)
#        return

    def isBusy(self):
        return False
    
    def atScanStart(self):
        print "atScanStart"
        self.warning_printed=False
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        #self.cli.caput(self.pvvalue)           # exclude early frames set to OFF

    def atPointStart(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        if not self.cli_exposures.isConfigured():
            self.cli_exposures.configure()
        exposures = int(self.cli_exposures.caget())
        if exposures > 1:
            if not self.warning_printed:
                print "WARNING: NOT forcing early frames to be excluded for this summing of %d exposures per image!" %(exposures)
                self.warning_printed=True
            self.cli.caput(0)
        else:
            self.cli.caput(self.pvvalue)
        #pass
        
    def atPointEnd(self):
        pass
    
    def stop(self):
        self.reset()
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()
        
#earlyFramesOFF_blurredsumOK=ExcludeEarlyFramesHandler('earlyFramesOFF_blurredsumOK', pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0)
#earlyFramesOFF=ExcludeEarlyFramesHandler('earlyFramesOFF', pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0)
earlyFramesIncluded=ExcludeEarlyFramesHandler('earlyFramesIncluded', pvname="BL12I-EA-DET-10:CAM:MotionBlur", pvvalue=0)

print "finished loading 'pixium10_utilities'"
