from org.eclipse.scanning.sequencer import ScanRequestBuilder
#from gdascripts.mscanHandler import submit
from java.net import URI
from org.eclipse.scanning.api.event.EventConstants import SUBMISSION_QUEUE
from mapping_scan_commands import submit
from org.eclipse.scanning.api.points.models import StaticModel
from org.eclipse.scanning.command.Services import getRunnableDeviceService
from org.eclipse.scanning.api.event.scan import DeviceState
import time
from org.eclipse.scanning.api.event.scan import ProcessingRequest
from java.lang import System
from org.eclipse.scanning.command.Services import getEventService
from gda.epics import CAClient
from java.util import HashMap

def burst(images, repeats, exposure_time=0.1):
    malc = getRunnableDeviceService().getRunnableDevice('BL18I-ML-SCAN-07')
    acq = CAClient("BL18I-DI-IOC-05:WRITE_MALC")
    acq.configure()
    p = ProcessingRequest()
    procMap = HashMap()
    procMap['i18-pyfai-burst'] = ['']
    p.setRequest(procMap)


    if exposure_time<0.002:
        print "Exposure Time too fast!"
    else:
        malc.getModel().setExposureTime(exposure_time)
        for r in range(repeats):
            print "Running: "+str(r+1)+"/"+str(repeats)

            request = ScanRequestBuilder().withPathAndRegion(StaticModel(images),None).withDetectors({malc.name : malc.model}).withProcessingRequest(p).build()

            try:
                print("Submitting")
                submit(request, block=False, name="Burst")
                print("Submitted")
                start=time.time()
                while(malc.getDeviceState()!=DeviceState.RUNNING):
                    passed=time.time()-start
                    time.sleep(0.01)
                    if passed>60:
                        break
                acq.caput(exposure_time)
                break_limit=60
                i=0
                while(malc.getDeviceState()!=DeviceState.READY):
                    time.sleep(1)
                    i+=1
                    if i>break_limit:
                        print "Timeout hit waiting for DeviceState to be READY"
                        break
                time.sleep(5)
                print("Repetition " + str(r + 1) + " complete")
            except Exception as e:
                print(e)


        print("Run complete")
