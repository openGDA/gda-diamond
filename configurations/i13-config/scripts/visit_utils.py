import os
import subprocess
import time
from gda.configuration.properties import LocalProperties
from i13i_utilities import wd, cfn, nfn, pwd, nwd, send_email

def disk_usage(path):
    """disk usage in human readable format (e.g. '2.1GB')"""
    #return subprocess.check_output(['du','-sh', path]).split()[0].decode('utf-8')
    return subprocess.check_output(['du','-sh', path]).split()[0]

def get_visit_root_path():
    #data_writer_path = LocalProperties.get("gda.data.scan.datawriter.datadir")
    data_writer_path = wd()
    data_writer_path_split = data_writer_path.rsplit('/')
    visit_path = '/'
    for i in range(1,6):
        visit_path = os.path.join(visit_path, data_writer_path_split[i])
    return visit_path

class VisitSummary:

    def __init__(self, visit_path=None, sub_dirs=None):
        self.configure(visit_path, sub_dirs)
        self.output_dct = {}
    
    def set_sub_dirs(self, sub_dirs):
        self.sub_dirs_lst = sub_dirs
        self.configure()
    
    def configure(self, visit_path, sub_dirs):
        self.sub_dirs_dct = {}
        if not visit_path is None:
            self.visit_path = visit_path
        else:
            self.visit_path = get_visit_root_path()
        #visit_path = wd()
        #self.visit_path = visit_path.encode('ascii', 'ignore') # str(...)
        
        if not sub_dirs is None:
            self.sub_dirs_lst = sub_dirs
        else:
            self.sub_dirs_lst = ['raw', 'processing']
        for subd in self.sub_dirs_lst:
            self.sub_dirs_dct.update({subd: os.path.join(self.visit_path, subd)})
    
    def update(self):
        self.configure(visit_path=None, sub_dirs=self.sub_dirs_lst)
        self.output_dct = {}
        # get disk usage
        for k, v in self.sub_dirs_dct.iteritems():
            if os.path.isdir(v):
                du = disk_usage(v)
                print v, du
                self.output_dct.update({v: du})
            else:
                msg = "Omitting %s as it is not a directory!" %(v)
                print msg
        
        out_str = ''
        for k, v in self.output_dct.iteritems():
            out_str += '%s \t %s' %(v, k)
            out_str += '\n'
        return out_str
    
    
    def report(self, emails=None):
        self.update()
        now = time.strftime("%c")
        out_str = 'Disk usage report for visit %s on %s:\n' %(self.visit_path, now)
        for k, v in self.output_dct.iteritems():
            out_str += '%s \t %s' %(v, k)
            out_str += '\n'
        if not emails is None:
            #send e-mail
            subj = 'Disk usage report for visit %s' %(self.visit_path)
            send_email(whoto=emails, subject=subj, body=out_str)
            pass
        print out_str

def reportVisit(emails=None):
    current_visit = VisitSummary()
    current_visit.report(emails)


from gda.device.scannable import ScannableBase
from gda.util import OSCommandRunner
from gdascripts.parameters import beamline_parameters

class ScanEndScriptRunner(ScannableBase):
    """
    Class that runs a script at scan end. 
    """
    def __init__(self, name, exepath, delay_sec=0):
        self.name = name
        self.inputNames = [name]
        self.exepath = exepath
        self.delay_sec = delay_sec
    
    def atScanEnd(self):
        time.sleep(self.delay_sec)
        jns=beamline_parameters.JythonNameSpaceMapping()
        lsdp=jns.lastScanDataPoint()
        #OSCommandRunner.runNoWait(["/dls/tmp/vxu94780/xscan.sh", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
        filepath = pwd()+'.nxs'
        print('Running script %s for Nexus scan file %s at the end of scan.' %(self.exepath,filepath))
        OSCommandRunner.runNoWait([self.exepath, filepath], OSCommandRunner.LOGOPTION.ALWAYS, None)

    def isBusy(self):
        return False
        
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawGetPosition(self):
        #return float('nan')
        return 0



#pixium_redux=ScanEndScriptRunner('pixium_redux', '/dls/tmp/vxu94780/xscan.sh')

from gda.data.metadata import GdaMetadata
from gda.factory import Finder
from __builtin__ import None
from datetime import datetime

def change_visit_id(visit_id):
    data_dir = os.path.join(os.sep+'dls',LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME),'data')     #/dls/i13/data
    sub_dir = 'raw'                     #can this be read from a property?
    year = str(datetime.now().year)

    #set output path
    data_path = os.path.join(data_dir,year,visit_id,sub_dir)
    print("GDA scan files will be saved in {}".format(data_path))
    LocalProperties.set("gda.data.scan.datawriter.datadir",data_path)

    #set visit in GDA metadata
    md = Finder.getInstance().findSingleton(GdaMetadata)	#Finder.findSingleton(GdaMetadata)
    md.setMetadataValue("visit", visit_id)




