import sys
import os
import stat
import time
import shutil
from tomographyScan import tomoScan, tomoFlyScan
#from i12utilities import pwd, cfn, getVisitRootPath, setSubdirectory, getSubdirectory
from i13j_utilities import pwd, cfn#, getVisitRootPath, setSubdirectory, getSubdirectory
from gdascripts.messages import handle_messages
from gda.jython.commands import ScannableCommands
from gdascripts.metadata.metadata_commands import setTitle, getTitle
from gdascripts.parameters import beamline_parameters
from gda.factory import Finder
from gda.configuration.properties import LocalProperties

try:
    print "Attempting to find ss1_X_dummy..."
    ss1_X_dummy = Finder.find("ss1_X_dummy")
    at = ss1_X_dummy()
    print "...found ss1_X_dummy at position: %s" %(at)
except:
    #ss1_X_dummy()   # will not print anything in Jython console
    print "Failed to find ss1_X_dummy"
    

def find_sub(sub, tgt):
    outind_lst = []
    ind = 0
    sub_len = len(sub)
    tgt_len = len(tgt)
    while ind < tgt_len:
        ind = tgt.find(sub, ind)
        if ind == -1:
            break
        #print("sub='%s' was found in tgt='%s' at ind=%i" %(sub, tgt, ind))
        outind_lst.append(ind)
        ind += sub_len
    return outind_lst

class NexusAudit:
    def __init__(self, bl, outdirpath="/dls/science/groups/das/NeXusAudit/", sig="-nexus_audit"):
        self.bl = bl	# used for adding sub-dir in /dls/science/groups/das/NeXusAudit/ixx (not used for paths of scan files)   
        self.signature = sig 
        self.outdirpath = self._handle_outdirpath(outdirpath) # pair
        self.filename_fmt = {'nxs_audit_tomo_step_scan': [{"%d.nxs": ["pco1-%d.hdf"]}]}

    def _handle_outdirpath(self, path):
        path_strippedspaces = path.strip()
        path_strippedrslashes = path_strippedspaces.rstrip("/")
        return (path_strippedrslashes, path_strippedrslashes + os.sep)

    def _to_string(self, preamble_fmt="string dump from an instance of class %s"):
        out = "\n Beginning " + preamble_fmt %(self.__class__.__name__) + "..."
        out += '\n'
        out += "bl = %s" %(self.bl)
        out += "\n"
        out += "outdirpath = %s" %(self.outdirpath,)
        out += "\n"
        out += "filename_fmt = %s" %(self.filename_fmt,)
        out += "\n"
        out += "\n ...finished " + preamble_fmt %(self.__class__.__name__) + "!\n"
        return out

    def add_filename_fmt_dct(self, item_dct):
        self.filename_fmt.update(item_dct)

#    def add_filename_fmt(self, funcname_key, indep_filenamepair_key, dep_filename_val):
#        if not funcname_key in self.filename_fmt:
 #           self.filename_fmt.update({funcname_key: []})
            
#        if not indep_filenamepair_key in self.filename_fmt[funcname_key]:
 #           self.filename_fmt[funcname_key].append({indep_filenamepair_key: []}) 
        
 #       self.filename_fmt[funcname_key].append(dep_filename_val)


    
         

nxs_audit = NexusAudit("i13-1") # for i13 Coherence branch
# scan can output multiple independent files and each of them may require multiple dependent files  
# key = function name
# val = list of dictionaries in which every key is a pair (of Nexus filename template and its destination filename) and every value is a list of dependent files    
#nxs_audit.add_filename_fmt_dct( {'function name': [{("nexus scan filename template","destination name for predecessor or empty string"): ["accompanying filename template 1", "accompanying filename template 1"]}]} )
#nxs_audit.add_filename_fmt_dct( {'nxs_audit_tomo_step_scan': [{("%d.nxs",""): ["projections_%d.hdf", "nothing"]}]} ) # useful for testing
nxs_audit.add_filename_fmt_dct( {'nxs_audit_tomo_step_scan': [{("%d.nxs",""): ["pco1-%d.hdf"]}]} )
#nxs_audit.add_filename_fmt_dct( {'nxs_audit_tomo_fly_scan': [{("%d.nxs",""): ["pco1-%d.hdf"]}]} )

print nxs_audit._to_string()

"""
def config_tomo_step_scan():
    jns = beamline_parameters.JythonNameSpaceMapping()
    obj_step = {}
    obj_step['tomography_theta'] = "jns.tomography_theta"
    obj_step['tomography_shutter'] = "jns.tomography_shutter"
    obj_step['tomography_translation'] = "jns.tomography_translation"
    
    obj_step_dummy = {}
    obj_step_dummy['tomography_theta'] = ss1_theta_dummy
    obj_step_dummy['tomography_shutter'] = eh1shtr_dummy
    obj_step_dummy['tomography_translation'] = ss1_x_dummy
    
    obj_step_backup = {}
    for key, val in obj_step.iteritems(): 
        obj_step_backup[key] = eval(val)
        
    for key, val in obj_step.iteritems(): 
        obj = eval(val)
        obj = obj_step_dummy[key]    
    
    return obj_step_backup
"""    
    
def wait4file(filepath, mode=os.R_OK, sleepdelta=1, niter=30):
    """
    Returns true if filename is found to exist after less than ntries. 
    sleepdelta is the time interval between checks
    """
    cnt = 0
    found = 0
    #wait for the directory to appear
    while (cnt < niter) and (found == 0):
        if not os.access(filepath, mode):
            cnt += 1
            time.sleep(sleepdelta)
            print "."
        else:
            found = 1
            print "File %s found on count = %i" %(filepath, cnt) 
    #exit if it times out
    return (os.access(filepath, mode), cnt)

def wait4file_NEW(filepath, mode=os.R_OK, sleepdelta=1, niter=30):
    """
    Waits for file to be accessible in given access mode
    Returns true if file was successfully accessed in given mode within specified number of attempts
    
    filepath: the path to file to be accessed 
    mode: the file mode in which file is to be accessed, eg os.R_OK
    sleepdelta: time interval in seconds between two consecutive attempts to access file; default=1, 
    niter: max number of access attempts to be made; default=30
    """

    cnt = 0
    failed = True # not_accessed
    #wait for file to be accessible in given mode
    while failed and (cnt < niter):
        if os.access(filepath, mode):
            failed = False
            print "File %s was successfully accessed on count = %i" %(filepath, cnt)
        else:
            cnt += 1
            time.sleep(sleepdelta)
            print " %i zzz..." %(cnt)
    return (not failed)        

def copy_single_file(src, dst, overwrite=False):
    success = False
    if not os.path.exists(src):
        msg = "Src file %s cannot be copied because it does not exist!" %(src)
        raise Exception(msg)
    if (not overwrite) and os.path.exists(dst):
        msg = "Dst file %s already exists (you may wish to delete it and then try copying it again)." %(dst)
        print msg
    else:
        try:
            shutil.copy(src, dst)
            success = True
            msg = "Success in copying src file %s to dst file %s" %(src, dst)
            print msg
        except:
            msg = "Failure in copying src file %s to dst file %s!" %(src, dst)
            print msg
    return success


def _handle_indep_fnames(src, dst, bupname):
    _src = src
    _dst = dst
    if not _src:
        msg = "NO NAME ON SRC: that's bad!"
        print msg
        #raise Exception(msg)

    if len(find_sub('%', _src)) != 1:
        msg = "DUBIOUS MULTIPLE FMTs ON SRC: that's bad!"
        print msg 
        #raise Exception(msg)
        
    _src_ext = os.path.splitext(_src)[1][1:].strip()
    if not _src_ext:
        msg = "NO EXT ON SRC: that's bad!"
        print msg
        #raise Exception(msg)

    _src_root = os.path.splitext(_src)[0][0:].strip()
    if not _src_root:
        msg = "NO ROOT ON SRC: that's bad!"
        print msg
        #raise Exception(msg)
        
    if not _dst:
        print "NO NAME ON DST: using src name!"
        #_dst = _src
        _dst = bupname
    _dst_ext = os.path.splitext(_dst)[1][1:].strip()
    if not _dst_ext:
        print "NO EXT ON DST: using src ext!"
        _dst_ext = _src_ext
        
    _dst_root = os.path.splitext(_dst)[0][0:].strip()
    if not ((nxs_audit.bl).lower() in _dst_root.lower()):
        #_dst_root = nxs_audit.bl + "-" + _dst_root
        _dst_root = nxs_audit.bl + ('-' if _dst_root else '') + _dst_root

    #_dst_root += "-" + "nexus-audit" # no need coz it should already be in bup (fun) name
    _dst = _dst_root + "." + _dst_ext
    return (_src, _dst)


# go through TO-DO before using this function
def nxs_audit_tomo_step_scan(outdirpath=None, runScan=True, sleepdelta=1, niter=30):
    """
    Desc:
    To run tomoScan and then copy the resulting scan files to the Nexus Audit dir or any specified output dir.
        Note: Depends on the presence of the nxs_audit object (defined at the top of this file) 
    Arg(s):
    outdirpath - abs path to output dir to which scan files are to be copied
        Note: if not None, this outdirpath will be used; otherwise nxs_audit.outdirpath will be used instead
    runScan - if True, tomoScan is run before copying the scan files produced by it; otherwise this function will attempt to copy the scan files of
        the most recent scan
        Note: if False, this function will look for the most recent scan files in the directory reported by getSubdirectory(), so the user is
            responsible for setting this sub-directory appropriately (with the help of setSubdirectory)
    sleepdelta - the interval of time (in sec) to wait (sleep) between two consecutive attempts to access a (single) scan file (before a copy attempt to dst dir)
    niter - max number of attempts (iterations) for accessing each scan file (before a copy attempt to dst dir)
    """
    thisfn = nxs_audit_tomo_step_scan.__name__
    print "Running %s..." %(thisfn)
    
    
    # use ss1_X_dummy for tomography_translation (defined in live_jythonNamespacemapping)
    # use ss1_rot_dummy for tomography_theta (defined in live_jythonNamespacemapping)
    # use pco1_hw_nochunking for tomography_detector (defined in live_jythonNamespacemapping)
    # use tomoScan command (note that other commands could be used instead, eg the vanilla 'scan' command)
    # 
    overall_success = True
    #subd_backup = getSubdirectory() # eg 'raw' as in /dls/ixx/data/2015/cm12345-1/raw/
    subd_backup = "raw" #TO-DO
    subd = "tmp"
    if runScan:
        print "Scan was requested to be run as runScan = %s" %(runScan)
        # set scan env
        #setSubdirectory(subd)       # eg /dls/ixx/data/2015/cm12345-1/tmp/
        LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/i13-1/data/2015/cm12164-3/tmp")  #TO-DO
        
        title_backup = getTitle()
        scan_title = "nexus_audit"
        setTitle(scan_title)	# tomoScan on i12 does it internally
        
        # select scan param(s)
        expoTime=0.2
        startAng=0.0
        stopAng=180.0
        stepAng=10.0

        addNXEntry=True
        autoAnalyse=False

        # run scan
        #tomoScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
        #      imagesPerDark=20, imagesPerFlat=20, min_i=-1., addNXEntry=True, autoAnalyse=True, tomography_detector=None, additionalScannables=[]):
        try:
            tomoScan(ss1_X_dummy(), ss1_X_dummy(), expoTime, \
                     startAng, stopAng, stepAng, \
                     darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=2, imagesPerFlat=2, \
                     min_i=-1., addNXEntry=addNXEntry, autoAnalyse=autoAnalyse, tomography_detector=None, additionalScannables=[])
            print "Finished running the scan!" 
        except:
            exceptionType, exception, traceback = sys.exc_info()
            handle_messages.log(None, "Exception in %s" %(thisfn), exceptionType, exception, traceback, False)
            overall_success = False
            raise
        finally:
            #setSubdirectory(subd_backup)
            #LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/i13-1/data/2015/mt11154-1/raw")  #TO-DO
            LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/i13-1/data/2015/cm12164-3/raw")  #TO-DO
            setTitle(title_backup)
    else:
        print "Scan was NOT requested to be run as runScan = %s (hence the most recent scan files will be used instead)" %(runScan)
        
    # work out relevant paths, eg /dls/ixx/data/2015/cm12163-1/rawdata/43860.nxs or /dls/ixx/data/2015/cm12163-1/tmp/43860.nxs
    # current file (scan) number
    fnum = cfn() # int
    #dir_src = getVisitRootPath() + os.sep + (subd if runScan else getSubdirectory()) + os.sep
    dir_src = "/dls/i13-1/data/2015/cm12164-3" + os.sep + (subd if runScan else "raw") + os.sep    #TO-DO    
    dir_dst = outdirpath
    if not dir_dst:
        dir_dst = nxs_audit.outdirpath[1]   # the one with trailing slash
    #dir_dst = "/dls/tmp/vxu94780/nexus_audit/i13-1/" # useful override for testing
    if (dir_dst in nxs_audit.outdirpath) and (not (nxs_audit.bl).lower() in dir_dst.lower()):
        dir_dst = os.path.join(dir_dst, nxs_audit.bl) # force-add subdirectory 'ixx'; no trailing slash
    
    print "dir_src = %s" %(dir_src)
    print "dir_dst = %s" %(dir_dst)
    
    # create dst directories, if necessary
    try:
        os.makedirs(dir_dst)
    except OSError, e:
        # dir already exists or is a file, or possibly some other type of errors
        if not os.path.isdir(dir_dst): # is file
            overall_success = False
            msg = "Output location %s is NOT a (accessible) directory!" %(dir_dst)
            print msg
            raise Exception(msg + " " +str(e))
    
    # enforce correct access permissions on dst_dir
    mode0777=0777
    try:
        os.chmod(dir_dst, mode0777)
        msg = "Success in chmod to mode = %o for dir %s" %(mode0777, dir_dst)
        print msg
    except:
        exceptionType, exception, traceback = sys.exc_info()
        msg = "Failure in chmod to mode = %o for dir %s" %(mode0777, dir_dst)
        handle_messages.log(None, msg, exceptionType, exception, traceback, False)
        print msg
    
    # create pairs of (src, dst) for all filename templates
    to_copy_fmt = []
    for fmt_dct in nxs_audit.filename_fmt[thisfn]:
        print "fmt_dct = ", fmt_dct
        for p, lst in fmt_dct.items():
            plen = len(p)
            if plen>0:
                _src_indep = p[0].strip()
            else:
                raise Exception("Key must NOT be an empty tuple!")
            if plen>1:
                _dst_indep = p[1].strip()
            else:
                _dst_indep = ""
            _src_indep_, _dst_indep_ = _handle_indep_fnames(_src_indep, _dst_indep, thisfn)
            to_copy_fmt.append((_src_indep_, _dst_indep_))
            for f in lst:
                _src_dep = f.strip()
                _dst_dep = _src_dep
                to_copy_fmt.append((_src_dep, _dst_dep))
            
    print "to_copy_fmt: ", to_copy_fmt

    # use filename templates to create filenames with actual scan number
    to_copy = []
    for p in to_copy_fmt:
        _pe_lst = []
        for pe in p:
            #_pe_lst = []
            if len(find_sub('%', pe))==1:
                try:
                    _pe_lst.append(pe %(fnum))
                except:
                    _pe_lst.append(pe)
            else:
                _pe_lst.append(pe)
        to_copy.append(tuple(_pe_lst))
    print "to_copy: ", to_copy
    
    for srcdst in to_copy:
        fname_src = srcdst[0]
        fname_dst = srcdst[1]
        
        fpath_src = os.path.join(dir_src, fname_src)
        fpath_dst = os.path.join(dir_dst, fname_dst)
        print "fpath_src = %s" %(fpath_src) 
        print "fpath_dst = %s" %(fpath_dst)
        fpath_exists = wait4file_NEW(fpath_src, sleepdelta=sleepdelta, niter=niter)
        if fpath_exists:
            print "File %s has been successfully accessed,\n and therefore can be copied to desired dst file %s" % (fpath_src, fpath_dst)
            print "Copying file %s to file %s..." % (fpath_src, fpath_dst)
            overall_success &= copy_single_file(fpath_src, fpath_dst, overwrite=True)
            # enforce correct access permissions on dst_file
            mode0666=0666
            try:
                os.chmod(fpath_dst, mode0666)
                msg = "Success in chmod to mode = %o for file %s" %(mode0666, fpath_dst)
                print msg
            except:
                exceptionType, exception, traceback = sys.exc_info()
                msg = "Failure in chmod to mode = %o for file %s" %(mode0666, fpath_dst)
                handle_messages.log(None, msg, exceptionType, exception, traceback, False)
                print msg
                overall_success = False
        else:
            overall_success = False
            print "File %s has NOT been successfully accessed,\n and therefore it will NOT be copied to desired dst file %s" % (fpath_src, fpath_dst)

    print "...finished running %s - bye!" %(thisfn)
    return overall_success




