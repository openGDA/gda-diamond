from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos, scan 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
import os
import subprocess
import shutil 
from gdascripts.parameters import beamline_parameters

from i12utilities import getVisitRootPath, wd, pwd, nwd, nfn, cfn

from gda.device.scannable import ScannableBase
from gda.util import OSCommandRunner
from gdascripts.parameters import beamline_parameters
from i12utilities import pwd

class ScanPtScriptRunner(ScannableBase):
    """
    Class that runs a script after each scan point in the fire-and-forget manner,
    ie without waiting for the script to complete.
    """
    def __init__(self, name, exepath, delay_sec=0.0):
        self.name = name                    #cbf and tif?
        self.inputNames = [name]
        self.exepath = exepath
        self.delay_sec = delay_sec
        self.min_idx_inc = 1
        self.idx_step_size = 1
        self.current_idx = self.min_idx_inc
        self.indirname_fmt = '%s-pilatus2M-files'
        #self.outdirname_fmt = '%s'                  #'%s-pilatus2M-files'
        self.min_npts_inc = 3
        self.dbg = False
        self.outdirpath = None
        self.indirpath = None
        self.ext = None			#cbf and tif
    
    def atPointEnd(self):
        sleep(self.delay_sec)
        if self.current_idx >= self.min_npts_inc:
            self.run_exe()
        self.current_idx += self.idx_step_size
    
    def gen_dirpaths(self, filepath=None, outdirpath=None):
        if filepath is None:
            fpath = pwd()+'.nxs'        #eg /dls/i12/data/2019/cm22974-1/rawdata/84757
            indirname = self.indirname_fmt %(cfn())
            h, t = os.path.split(fpath)
            indirpath = os.path.join(h, indirname)
        else:
            fpath = filepath
        
        if outdirpath is None:
            h, t = os.path.split(fpath)
            b, ext = os.path.splitext(t)
            outdirpath = '/'.join(h.split('/')[:-1])
            outdirpath = os.path.join(outdirpath, 'tmp', 'dawn', b)
        return indirpath, outdirpath
    
    def run_exe(self, filepath=None, outdirpath=None):
        """
        To generate a DAWN linking file on demand (as opposed to it being generated automatically during the scan),
        eg pilatus_dawn.run_exe("/dls/i12/data/2019/cm22974-1/rawdata/84780.nxs")
        Arg(s):
        filepath: path to Nexus scan file; default=None (ie the most-recent GDA scan file, eg /dls/i12/data/<year>/<visit>/rawdata/<scan number>.nxs)
        outdirpath: path to the output directory; default=None (ie /dls/i12/data/<year>/<visit>/tmp/dawn/<scan number>, which is derived from the above filepath argument)
            Note: the gda2 user needs to have write permissions in outdirpath 
        """
        #jns=beamline_parameters.JythonNameSpaceMapping()
        #lsdp=jns.lastScanDataPoint()
        #OSCommandRunner.runNoWait(["/dls/tmp/vxu94780/xscan.sh", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        #python gen-linkingfile.py -b 1 -n 10 /dls/i12/data/2019/cm22974-1/rawdata/84757-pilatus2M-files/ /dls/i12/data/2019/cm22974-1/tmp
#        if filepath is None:
#            fpath = pwd()+'.nxs'		#eg /dls/i12/data/2019/cm22974-1/rawdata/84757
#            indirname = self.indirname_fmt %(cfn())
#            h, t = os.path.split(fpath)
#            indirpath = os.path.join(h, indirname)
#        else:
#            fpath = filepath
#        
#        if outdirpath is None:
#            h, t = os.path.split(fpath)
#            b, ext = os.path.splitext(t)
#            outdirpath = '/'.join(h.split('/')[:-1])
#            outdirpath = os.path.join(outdirpath, 'tmp', 'dawn', b)
#        self.outdirpath = outdirpath
        self.indirpath, self.outdirpath = self.gen_dirpaths(filepath=filepath, outdirpath=outdirpath)
        cmd = 'python %s -b %d -n %d -f %s %s %s' %(self.exepath, 0, self.current_idx, self.ext, self.indirpath, self.outdirpath)
        if self.dbg:
            cmd += ' --dbg'
        if not self.dbg:
            os.system(cmd)
        else:
            #print('@ScanPt %d: cmd %s' %(self.current_idx,cmd))
            proc = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
            result = proc.communicate()
            #print result
            res = result[0].split('\n')
            #print len(res)
            for i, each in enumerate(res):
                print i, each
        # OSCommandRunner.runNoWait([self.exepath, fpath], OSCommandRunner.LOGOPTION.ALWAYS, None)
    
    def isBusy(self):
        return False
        
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawGetPosition(self):
        #return float('nan')
        return 0
    
    def stop(self):
        self.current_idx = self.min_idx_inc
        
#    def setup(self):
#        setup_pilatus_postprocessing()
    
    def atScanStart(self):
        self.outdirpath = None
        self.indirpath = None
        self.indirpath, self.outdirpath = self.gen_dirpaths(filepath=None, outdirpath=None)
        if not self.outdirpath is None:
            print("*** Path to directory containing this scan's DAWN linking file: %s" %(self.outdirpath))
        from gda.jython import InterfaceProvider
        self.ext = None
        det_names = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation().getDetectorNames()
        if len(det_names)>0:
            if 'cbf' in det_names[0]:
                self.ext = "*.cbf"
            elif 'tif' in det_names[0]:
                self.ext = "*.tif"  #not tiff
        if self.ext is None:
            self.ext = "*"
    
    def atScanEnd(self):
        if not self.outdirpath is None:
            print("*** Path to directory containing this scan's DAWN linking file: %s" %(self.outdirpath))
        self.current_idx = self.min_idx_inc
    
    def atCommandFailure(self):
        self.current_idx = self.min_idx_inc

pilatus_dawn=ScanPtScriptRunner('pilatus_dawn', '/dls_sw/i12/software/gda/config/scripts/gen_dawn_linkingfile.py')


from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase

class CamArrayCallbacksHandler(ScannableMotionBase):
    # constructor
    def __init__(self, name, pvname="BL12I-EA-PILAT-01:CAM:ArrayCallbacks", pvvalue=1):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%d"])
        self.pvvalue=int(pvvalue)
        self.pvname=pvname
        self.cli=CAClient(pvname)
        self.cli_timeout=CAClient("BL12I-EA-PILAT-01:CAM:ImageFileTmot")
        self.backup_pos=None
        self.current_pos=None
        self.timeout_backup_pos=None
        self.timeout_current_pos=None
        self.warning_printed=False
        
    def reset(self):
        if not self.cli.isConfigured():
            self.cli.configure()
        if self.backup_pos is not None:
            self.cli.caput(self.backup_pos)
            self.current_pos=self.backup_pos
        if not self.cli_timeout.isConfigured():
            self.cli_timeout.configure() 
        if self.timeout_backup_pos is not None:
            self.cli_timeout.caput(self.timeout_backup_pos)
            self.timeout_current_pos=self.timeout_backup_pos

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
#    def isBusy(self):
#        #print "hello from isBusy"
#        sleep(1)
#        return

    def isBusy(self):
        return False
    
    def atScanStart(self):
        #print "atScanStart"
        self.warning_printed=False
        if not self.cli.isConfigured():
            self.cli.configure()
        self.backup_pos=self.cli.caget() 
        self.current_pos=self.backup_pos
        #self.cli.caput(self.pvvalue)           # exclude early frames set to OFF
        if not self.cli_timeout.isConfigured():
            self.cli_timeout.configure()
        self.timeout_backup_pos=self.cli_timeout.caget() 
        self.timeout_current_pos=self.timeout_backup_pos
        self.cli_timeout.caput(0.1)

    def atPointStart(self):
        #print "atPointStart"
        if not self.cli.isConfigured():
            self.cli.configure()
        self.cli.caput(self.pvvalue)
        if not self.cli_timeout.isConfigured():
            self.cli_timeout.configure()
        self.cli_timeout.caput(0.1)
        
    def atPointEnd(self):
        pass
    
    def stop(self):
        self.reset()
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()
        

pilatus_preview_on=CamArrayCallbacksHandler('pilatus_preview_on', pvname="BL12I-EA-PILAT-01:CAM:ArrayCallbacks", pvvalue=1)

        
print "finished loading 'pilatus_utilities'"
