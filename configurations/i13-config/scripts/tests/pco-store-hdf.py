#!/dls_sw/prod/tools/RHEL5/bin/dls-python2.6

from pkg_resources import require
require("cothread")
import cothread
from cothread.catools import *

class StoreHdf:
    def __init__(self, pv_pco, pv_hdf):
        self.pv_pco = pv_pco
        self.pv_hdf = pv_hdf
        
    def init_plugin(self):
        # Set the hdf plugin in stream mode
        caput( self.pv_hdf + ":FileWriteMode", "Stream", wait=True)
        # enable the plugin
        caput( self.pv_hdf + ":EnableCallbacks", 1, wait=True)
        # Set the hdf plugin in blocking mode (optional)
        caput( self.pv_hdf + ":BlockingCallbacks", 1, wait=True)
        
        # Pull one image from the driver though to the hdf plugin
        # without storing it. This is to initialise the dimensions of the dataset
        # Not exactly an ideal solution - but this is how every areaDetector
        # file writer works!
        caput( self.pv_pco + ":ImageMode", "Single", wait=True)
        
        #### any other pco camera config necessary here????
        
        # Trigger the camera for one image and wait for it to complete
        print "Pulling one frame through to initialise the HDF plugin"
        print "This frame will *not* be stored in file!"
        caput( self.pv_pco + ":Acquire", 1, wait=True, timeout = 10.0)
        return True
        
    def configure_destination(self, directory, fileprefix):
        # Set the filename format
        caput( self.pv_hdf + ":FileTemplate", "%s%s_%04d.h5", datatype=DBR_CHAR_STR, wait=True)
        # Set the file path
        caput( self.pv_hdf + ":FilePath", directory, datatype=DBR_CHAR_STR, wait=True)
        # TODO: check the HDF:FilePathExists_RBV PV to ensure the file path is visible to the IOC
        if not caget( self.pv_hdf + ":FilePathExists_RBV" ):
            print "ERROR: the directory %s does not exist" % directory
            return False
        
        # Set the file prefix
        caput( self.pv_hdf + ":FileName", fileprefix, datatype=DBR_CHAR_STR, wait=True)
        return True
        
    def capture(self, num_frames=1):
        # set the pco camera to capture num_frames
        caput( self.pv_pco + ":NumImages", num_frames, wait=True)
        caput( self.pv_pco + ":ImageMode", "Multiple", wait=True)
        # set the hdf plugin to write num_frames to disk
        caput( self.pv_hdf + ":NumCapture", num_frames, wait=True)
        # 'start' the HDF5 plugin: i.e. open the file in preparation to write incoming frames
        print "Starting the HDF5 plugin: i.e. opening file for writing"
        caput( self.pv_hdf + ":Capture", 1, wait=False)
        # Wait for the capture readback field to indicate that the file is open and ready
        # Also check the WriteStatus field to check that an error didn't occur in creating the file
        # Here we do this by polling - it could be done more elegantly with a monitor
        while( caget( self.pv_hdf + ":Capture_RBV" ) != 1):
            cothread.Sleep(0.2)
            if (caget( self.pv_hdf + ":WriteStatus") != 0):
                print "Error in opening file. Aborting."
                return False
        
        # Start the camera running
        print "Starting the camera to capture %d frames"%num_frames
        caput( self.pv_pco + ":Acquire", 1, wait=False )
        # Wait for the camera to start acquiring. Again with polling but could be done with monitors
        while( caget( self.pv_pco + ":Acquire" ) != 1 ):
            cothread.Sleep(0.1)
        
        # Monitor both driver and hdf plugin to check they're running.
        print "Acquisition and capture running..."
        pco_running = True
        hdf_running = True
        while( pco_running and hdf_running ):
            cothread.Sleep(0.1)
            pco_running = (caget( self.pv_pco + ":Acquire" ) == 1)
            hdf_running = (caget( self.pv_hdf + ":Capture_RBV") == 1)
            
        if not hdf_running:
            print "HDF plugin stopped after %d frames" % caget( self.pv_hdf+":NumCaptured_RBV" )
            # Stop the camera in case it's still running
            caput( self.pv_pco + ":Acquire", 0, wait=True)
            
        if not pco_running:
            print "PCO camera stopped acquiring after %d frames" % caget(self.pv_pco + ":NumImagesCounter_RBV")
        return True
        
        
        
def main():
    ad = StoreHdf( "BL13I-EA-DET-01:CAM", "BL13I-EA-DET-01:HDF" )
    if not ad.init_plugin():
        return
    if not ad.configure_destination( "C:/pco_cam", "hdftest" ):
        return
    if not ad.capture( 10 ):
        return
    
if __name__=="__main__":
    main()
    
