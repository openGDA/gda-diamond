from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos, scan 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
import os
import shutil 
from gdascripts.parameters import beamline_parameters
from gda.factory import Finder

from i12utilities import getVisitRootPath

try:
    pixium10_hdf=Finder.find("pixium10_hdf")
    pixium10_tif=Finder.find("pixium10_tif")
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
from gda.device.scannable import ScannableMotionBase

class ExcludeEarlyFramesDefaultHandler(ScannableMotionBase):
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
            self.cli.caput(self.current_pos)
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


class ExcludeEarlyFramesHandler(ScannableMotionBase):
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
            self.cli.caput(self.current_pos)
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

from gda.device.scannable import ScannableBase
from gda.util import OSCommandRunner
from gdascripts.parameters import beamline_parameters
from i12utilities import pwd

class ScanEndScriptRunner(ScannableBase):
    """
    Class that runs a script at scan end, without waiting for the script's completion (fire-and-forget).
    """
    def __init__(self, name, exepath, delay_sec=0):
        self.name = name
        self.inputNames = [name]
        self.exepath = exepath
        self.delay_sec = delay_sec
    
    def atScanEnd(self):
        sleep(self.delay_sec)
        self.run_exe()

    def run_exe(self, filepath=None):
        """
        To run post-processing on demand (as opposed to it being run automatically), eg
        difract_redux.run_exe("/dls/i12/data/2017/cm1234-5/rawdata/6789.nxs")
        """
        #jns=beamline_parameters.JythonNameSpaceMapping()
        #lsdp=jns.lastScanDataPoint()
        #OSCommandRunner.runNoWait(["/dls/tmp/vxu94780/xscan.sh", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        if filepath is None:
            fpath = pwd()+'.nxs'
        else:
            fpath = filepath 
        print('Executing script %s for Nexus scan file %s at the end of scan.' %(self.exepath,fpath))
        OSCommandRunner.runNoWait([self.exepath, fpath], OSCommandRunner.LOGOPTION.ALWAYS, None)

    def isBusy(self):
        return False
        
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawGetPosition(self):
        #return float('nan')
        return 0
    
    def stop(self):
        sleep(self.delay_sec)
        self.run_exe()
        
    def setup(self):
        setup_pixium_postprocessing()
        

difract_redux=ScanEndScriptRunner('difract_redux', '/dls_sw/apps/dawn_autoprocessing/autoprocess')


def setup_pixium_postprocessing(dst_dir=None):
    """
    To create the 'templates' sub-directory in /dls/i12/data/<yyyy>/<visit-id>/xml, and then 
    to populate it 
    
    Arg(s)
    dst_dir: if None, then the 'templates' sub-directory is created in /dls/i12/data/<yyyy>/<visit-id>/xml
             if not None, then the 'templates' sub-directory is created in the input directory (useful for testing) 
    """
    # check permissions!
    print("Setting up the post-processing pipeline for PIXIUM...")
    if dst_dir is None:
        dst_dir = os.path.join(getVisitRootPath(),'xml','templates')
    else:
        dst_dir = dst_dir
    print(" ...attempting to create %s directory for the post-processing pipeline..." %(dst_dir))
    try:
        os.mkdir(dst_dir) # not using makedirs coz not expecting a deeper structure
        msg = " ...created a new %s directory" %(dst_dir)
        print msg
    except OSError, e:
        msg = " ...directory %s already exists" %(dst_dir)
        print msg
        if not os.path.isdir(dst_dir):
            msg = " ...output location %s is not a directory!" %(dst_dir)
            print msg
            raise Exception(msg + str(e))
    # copy all json files, if they are not already there (it would be much better to list and count only .json.files!)
    if len(os.listdir(dst_dir)) == 0:
        # copy json files
        src_dir = '/dls_sw/i12/scripts/pixium_reduction'
        count = 0
        for src_fname in os.listdir(src_dir):
            msg = " ...attempting to copy all JSON files from %s to %s" %(src_dir, dst_dir)
            print msg
            if src_fname.endswith('.json'):
                src_fpath = os.path.join(src_dir, src_fname) 
                dst_fpath = os.path.join(dst_dir, src_fname)
                shutil.copy(src_fpath, dst_fpath)
                count += 1
           
        msg = " ...copied %d JSON files from %s to %s" %(count, src_dir, dst_dir)
        print msg
    print("Finished setting up the post-processing pipeline for PIXIUM!")

#from gda.epics import CAClient
import gda.scan.ScanInformation as si
class PixiumAcquireTimeHandler(ScannableMotionBase):
    # constructor
    def __init__(self, name, pvname="BL12I-EA-DET-10:CAM:AcquireTime"):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%.3f"])
        self.pvname=pvname
        self.cli_acquire_time=CAClient(pvname)
        self.cli_acquire_period=CAClient("BL12I-EA-DET-10:CAM:AcquirePeriod")
        self.cli_calibration_running=CAClient("BL12I-EA-DET-10:CAM:Calibrate_RBV")
        self.cli_exposures_per_image=CAClient("BL12I-EA-DET-10:CAM:NumExposures")
        self.cli_images=CAClient("BL12I-EA-DET-10:CAM:NumImages")
        self.delegate=pixium10_tif
        
    def configureAll(self):
        if not self.cli_acquire_time.isConfigured():
            self.cli_acquire_time.configure()
        if not self.cli_acquire_period.isConfigured():
            self.cli_acquire_period.configure()
        if not self.cli_calibration_running.isConfigured():
            self.cli_calibration_running.configure()
        if not self.cli_exposures_per_image.isConfigured():
            self.cli_exposures_per_image.configure()
        if not self.cli_images.isConfigured():
            self.cli_images.configure()    
    
    def clearupAll(self):
        if self.cli_acquire_time.isConfigured():
            self.cli_acquire_time.clearup()
        if self.cli_acquire_period.isConfigured():
            self.cli_acquire_period.clearup()         
        if self.cli_calibration_running.isConfigured():
            self.cli_calibration_running.clearup()            
        if self.cli_exposures_per_image.isConfigured():
            self.cli_exposures_per_image.clearup()            
        if self.cli_images.isConfigured():
            self.cli_images.clearup()            
    
    # returns the value this scannable represents
    def rawGetPosition(self):
        if not self.cli_acquire_time.isConfigured():
            self.cli_acquire_time.configure()
        return self.cli_acquire_time.caget()

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return
        print("* rawAsynchronousMoveTo %.3f" %(new_position))
        if not self.cli_acquire_time.isConfigured():
            self.cli_acquire_time.configure()
        if not self.cli_acquire_time.isConfigured():
            self.cli_acquire_period.configure()
        if not self.cli_exposures_per_image.isConfigured():
            self.cli_exposures_per_image.configure()
        if not self.cli_images.isConfigured():
            self.cli_images.configure()    

        current_pos=float(self.cli_acquire_time.caget())
        cs = pixium10_tif.getCollectionStrategy() 
        if new_position is not None:
            eps = 0.0001
            #if abs(current_pos - new_position) > eps:
            if (current_pos - new_position) > eps:
                self.cli_acquire_time.caput(new_position)
                self.cli_acquire_period.caput(new_position)
                print("...calibration REQUIRED to a new base acquire time %.3f" %(new_position))
                self.delegate.calibrate()
                cs.prepareForCollection(float(new_position), 1, None)
                print("... (c1) preparing for collection with acquire time %.3f and the new base acquire time %.3f" %(new_position, new_position))
            else:
                print("...NO need to re-calibrate for collection with acquire time %.3f and the current base acquire time %.3f" %(new_position, current_pos))
                if abs(current_pos - new_position) > eps:
                    print("...(c2) preparing for collection with acquire time %.3f and the current base acquire time %.3f" %(new_position, current_pos))
                    #si_tmp = si.ScanInformation()
                    cs.prepareForCollection(float(new_position), 1, None)
                else:
                    print("...(c3) preparing for collection with acquire time %.3f and the current base acquire time %.3f" %(new_position, current_pos))
                    #cs.prepareForCollection(float(new_position), 1, None)
                    #self.cli_acquire_time.caput(float(new_position))
                    self.cli_exposures_per_image.caput(1)
                    self.cli_images.caput(1)
        return

    # Returns the status of this Scannable
#    def rawIsBusy(self):
#        #print "hello from rawIsBusy"
#        sleep(1)
#        return

    def isBusy(self):
        #print "isBusy"
        if not self.cli_calibration_running.isConfigured():
            self.cli_calibration_running.configure()
        current_state = self.cli_calibration_running.caget()
        return int(current_state) != 0
    
    def atScanStart(self):
        print "* atScanStart"
        self.configureAll()

    def atPointStart(self):
        pass
        
    def atPointEnd(self):
        pass
    
    def stop(self):
        self.clearupAll()
    
    def atScanEnd(self):
        self.clearupAll()
    
    def atCommandFailure(self):
        self.clearupAll()

pixium10_acquire_time_handler = PixiumAcquireTimeHandler(name='pixium10_acquire_time_handler')
        
print "finished loading 'pixium10_utilities'"
