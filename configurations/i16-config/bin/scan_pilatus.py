#!/dls_sw/prod/tools/RHEL5/bin/python2.6
'''
Created on 18 Jun 2010

repeats exposure of Pilatus and outputs time per point 

@author: tjs15132
'''
from pkg_resources import require
require('cothread')
from cothread import *
from cothread.catools import *
import sys
from optparse import OptionParser
import time
from datetime import datetime
from PIL import Image
import os.path

class TimeoutError(Exception):
    pass

class PilatusScan:
    usage_text = """scan_pilatus -p epics_pv_base -t exposure_time -n num_exposures -l -w wait_timeout --o results_file"""

    def usage(self):
        print "usage: %s" % self.usage_text

    def __init__(self, argv):
        self.output = None
        parser = OptionParser(usage=self.usage_text)
        parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="increase verbosity")
        parser.add_option("-p", "--pv", dest="pv", type="string", default="unknown", help="the pv of the Pilatus")
        parser.add_option("-t", "--exposure_time", dest="exposure_time", type="float", default=1.0, help="exposure time in seconds (default 1.0)")
        parser.add_option("-n", "--num_exposures", dest="num_exposures", type="int", default=10, help="number of exposures (default 10)")
        parser.add_option("-l", "--load_images", dest="load_images", action="store_true", default=False, help="load image before following exposure")
        parser.add_option("-w", "--wait_timeout", dest="wait_timeout", type="float", default=60.0, help="timeout for image to appear or load")
        parser.add_option("-r", "--record_pv", dest="record_pv", type="string", default="unknown", help="the base pv for recording. e.g. BL16I-EA-IOC-10  ")
        parser.add_option("-o", "--output", dest="output", type="string", default=10, help="file name for timing results")
        (self.options, args) = parser.parse_args(argv)
        print self.options
        print args
        if len(args) != 0:
            self.usage()
            sys.exit(1)
            
        
        self.image_directory = self.readImageDirectory()
        self.image_base_name = str(caget(self.options.pv+":Filename"))
        self.image_format  = str(caget(self.options.pv+":FileFormat"))
        
    def readImageDirectory(self):
    	bytelist = caget(self.options.pv+":FilePathArray")
    	path = ''.join([chr(v) for v in list(bytelist) if v not in [0]])
    	if self.options.verbose:
            print "Image directory: ", path
        return path
        

            
    def run(self):
        try:
            initial_file_number = int(caget(self.options.pv+":FileNumber"))
            self.set_exposure_time()
            time_at_start_of_run = time.time()
            if self.options.output != None:
                self.output = open(self.options.output,"w")
    
            self.log("time, i, file_number, time_since_start, n_stats, t_expose, t_available, t_load, t_total")
             
            for i in range(self.options.num_exposures):
                #isotime = datetime.now().isoformat()
                time_since_epoch = time.time()
                time_before_exposure = time.time()
                time_since_start = time_before_exposure - time_at_start_of_run
                self.start_exposure()
                self.waitWhileBusy()
                time_after_exposure = time.time()
                t_expose = time_after_exposure - time_before_exposure
                if self.options.load_images:
                    imagePath = self.image_format % (self.image_directory, self.image_base_name, initial_file_number + i)
                    try:
                        n_stats = self.waitForFileAvailable(imagePath) # might timeout
                        time_after_available = time.time()
                        t_available = time_after_available - time_after_exposure
                        self.loadFile(imagePath)
                        time_after_loaded = time.time()
                        t_load = time_after_loaded - time_after_available
                        t_total = time_after_loaded - time_before_exposure
                    except TimeoutError, e:
                        t_available = 9999
                        t_load = 9999
                        t_total = 9999
                        
                else:
                    t_available = -1
                    t_load = -1
                    t_total = t_expose
                    n_stats = 0

                self.log("%f, %d, %d, %f, %d, %f, %f, %f, %f" % (time_since_epoch, i, initial_file_number + i, time_since_start, n_stats, t_expose, t_available, t_load, t_total))
                if self.options.record_pv:
                    self.record_stats_to_pvs(t_expose, t_available, t_load, t_total)
        finally:
            if self.output is not None:
                self.output.close()

    def record_stats_to_pvs(self, twrite, tavail, tload, tacquire):
		caput(self.options.record_pv + ":TWRITE",twrite)
		caput(self.options.record_pv + ":TAVAIL",tavail)
		caput(self.options.record_pv + ":TLOAD",tload)
		caput(self.options.record_pv + ":TACQUIRE",tacquire)

    def log(self,s):
        print s
        if self.output != None:
            self.output.write(s+"\n")
            self.output.flush()

    def set_exposure_time(self):
        if self.options.verbose:
            print "setExposure"
        caput(self.options.pv+":ExposureTime", self.options.exposure_time)
    
    def start_exposure(self):
        if self.options.verbose:
            print "start_exposure"
        caput(self.options.pv+":Acquire",1)
        
    def waitWhileBusy(self):
        if self.options.verbose:
            print "waitWhileBusy"
        acquire = bool(caget(self.options.pv+":Acquire"))
        while(acquire):
#            if self.options.verbose:
#                print "wait for 0.05s"
            time.sleep(0.05)
            acquire = bool(caget(self.options.pv+":Acquire"));

    def waitForFileAvailable(self, imagePath):
        if self.options.verbose:
            print "Waiting for file to appear: ", imagePath
        time_poll_start = time.time()
        n_stats = 1
        while(not os.path.exists(imagePath)):
            n_stats += 1
            time.sleep(0.05)
            if (time.time() - time_poll_start) > self.options.wait_timeout:
                raise TimeoutError("Timed out after %fs waiting for file to appear: %s" % (self.options.wait_timeout, imagePath))
        return n_stats

    def loadFile(self, imagePath):
        if self.options.verbose:
            print "Loading file: ", imagePath
        file_extension = imagePath.split('.')[-1].lower()
        if file_extension is 'cbf':
            # just load as binary file
            file = open(imagePath, 'r')
            file.close()
        else:
            image = Image.open(imagePath)
            image.getextrema()

def main(*arguments):
    PilatusScan(*arguments).run()

if __name__ == '__main__':
    main(sys.argv[1:])
