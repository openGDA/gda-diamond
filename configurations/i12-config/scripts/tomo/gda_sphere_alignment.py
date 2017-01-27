from gdascripts.parameters import beamline_parameters
from gda.jython import InterfaceProvider
from tomo.sphere_alignment_processing import sphere_alignment_processing as s_alignment_processing
import scisoftpy as dnp
import time
import os

tomopos=0
flatpos=-25
def request_GDA_Input():
    pass

def acquire_align_data(expo):
    jns = beamline_parameters.JythonNameSpaceMapping()
    tomomotor = jns.sphere_align_tomomotor
    if tomomotor is None:
        raise "sphere_align_tomomotor is not defined in Jython namespace"
    samplemotor = jns.sphere_align_samplemotor
    if samplemotor is None:
        raise "sphere_align_samplemotor is not defined in Jython namespace"
    print tomomotor.getName()
    visit_folder=getVisitRootPath()
    input_folder=getSubdirectory()
    pos samplemotor tomopos
    setTitle("Alignment data scan")
    scan tomomotor 0 360 20 pco4000_dio_hdf expo
    scannum=cfn()
    scanname="%s.nxs"%scannum

    pos samplemotor flatpos
    setTitle("Alignment flatfield scan")

    scan ix 0 10 1 pco4000_dio_hdf expo
    setTitle("No title set")
    flatnum=cfn()
    flatname="%s.nxs"%flatnum
    print "Acquired alignment data in visit_folder:",visit_folder,"subdirectory",input_folder
    print "alignment scan:", scanname
    print "flat field scan:",flatname
    return(visit_folder,input_folder,scannum,flatnum)


def wait_for(fullpath):
    done=0
    ntries=0
    while (done==0 and ntries < 1000):
        if (ntries % 50 == 0):
            print "Waiting for %s"%fullpath
        aa= os.access(fullpath, os.R_OK)
        print "access:",aa   
        if aa:
            done=1
        else:
            ntries += 1
        time.sleep(1)
    if (ntries >= 1000):
        print "time-out exceeded!"
        return(1)
    return(0)

def wait_for_netapp(visit_folder,input_folder,scannum,flatnum):
    flatfilename="%s/%s/projections_%s.hdf"%(visit_folder,input_folder,flatnum)
    scanfilename="%s/%s/projections_%s.hdf"%(visit_folder,input_folder,scannum)
    fres=wait_for(flatfilename)
    if (fres != 0 ):
        print "waiting for %s didn't work"%flatfilename
        return(1)
    sres=wait_for(scanfilename)
    if (sres != 0):
        print "waiting for %s didn't work"%flatfilename
        return(1)
    return(0)

def test_stub(expo=0.1):
    (visit_folder,input_folder,scannum,flatnum)=acquire_align_data(expo)
    result=wait_for_netapp(visit_folder,input_folder,scannum,flatnum)
    print "Return value was ", result
    
    if result != 0 :
        return(result)
    else:
        rx,rz,xarray,zarray=s_alignment_processing(False,visit_directory=visit_folder,flatfile=flatnum, projectionfile=scannum, threshold=0.4, max_tries=15,prompt=False,testdata=False, request_input_command=request_GDA_Input)
    return(0)

print "Function acquire_align_data() added to the environment"