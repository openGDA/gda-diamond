'''
Created on 7 Aug 2019

@author: fy65
'''

from externalProcess.external import create_function
from gda.device.scannable import ScannableMotionBase
from gda.jython import InterfaceProvider
from time import sleep
import time

#Path to Python modules to run as external processing
image_process_module_path='/dls_sw/lab44/scripts/GavinHill/Current_code'

#Python library path
python_path="/dls_sw/apps/python/anaconda/1.7.0/64/lib/python2.7/"
#Python executable path to run external process
python_exe="/dls_sw/apps/python/anaconda/1.7.0/64/bin/python"


class ImageProcessor(ScannableMotionBase):
    '''
    kick off image processing following a scan data collection with area detector camera
    '''

    def __init__(self, name):
        '''
        Constructor
        '''
        self.setName(name)
        #No input no output scannable
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])
        #create function to run external python process
        self.processStitch=create_function("processStitch",module="startImageProcessing", exe=python_exe, path=[python_path], extra_path=[image_process_module_path], keep=False)
        self.process_stitching=False
        self.returns=None
        self.firstTime=True
     
    def atScanEnd(self):
        info=InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
        scanfilename=info.getFilename()
        scanNumber=info.getScanNumber()
        print(scanfilename)
        print(scanNumber)
        
        self.returns=None
        self.firstTime=True
        if self.process_stitching:
            self.returns=self.processStitch(scanfilename, scanNumber)
            self.process_stitching=False
        print self.returns
        
    def getResults(self):
        while not self.returns:
            if self.firstTime:
                print "Waiting for image process results ..."
                self.firstTime=False
            sleep(0.1)
        return self.returns
    
    def stop(self):
        if self.process_stitching:
            self.processStitch.stop()
            
    def asynchronousMoveTo(self, newpos):
        pass
    
    def getPosition(self):
        pass
    
    def isBusy(self):
        return False   

processImages=ImageProcessor("processImages")

# if __name__=='__main__':
#     scanfilename = "/dls/i06/data/2019/cm22966-3/processing/optical_microscope/lab44-92.nxs"
#     scanNumber = 92
#     starttime=time.time()
#     print "process starts at %f" % starttime
#     image_data_path = processImages.processStitch(scanfilename, scanNumber)
#     endtime=time.time()
#     print "process end at %f"  % endtime
#     print "total time taken is %f " % (endtime-starttime)
#     print image_data_path
