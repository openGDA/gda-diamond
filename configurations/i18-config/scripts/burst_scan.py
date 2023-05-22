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
    # Specific scan made for burst mode
    malc = getRunnableDeviceService().getRunnableDevice('BL18I-ML-SCAN-07')
    # Get the PV for writing the exposure time to malcolm
    acq = CAClient("BL18I-DI-IOC-05:WRITE_MALC")
    acq.configure()
    p = ProcessingRequest()
    procMap = HashMap()
    procMap['i18-pyfai-burst'] = ['']
    p.setRequest(procMap)

    # Check the exposure time provided is not less than 0.002 as this is too fast
    # for the detector
    if exposure_time<0.002:
        print "Exposure Time too fast!"
    else:
        malc.getModel().setExposureTime(exposure_time)
        for r in range(repeats):
            print "Running: "+str(r+1)+"/"+str(repeats)

            request = ScanRequestBuilder().withPathAndRegion(StaticModel(images),None).withDetectors({malc.name : malc.model}).withProcessingRequest(p).build()

            try:
                print("Submitting")
                # Submit the scan to malcolm without blocking so we can monitor the progress
                submit(request, block=False, name="Burst")
                print("Submitted")
                start=time.time()
                break_limit=60
                # Wait for the scan to start running - this should not take more than 60 seconds
                # If this takes longer than 60 seconds then the DeviceState may have gone into a state other than RUNNING
                while(malc.getDeviceState()!=DeviceState.RUNNING):
                    passed=time.time()-start
                    time.sleep(0.01)
                    if passed>break_limit:
                        break
                # Set the exposure time after the scan has started running
                # If the scan has failed or something has gone wrong and the DeviceState is not
                # RUNNING then setting the exposure time will not do any harm so no checks are necessary
                acq.caput(exposure_time)
                # Wait for the device state to return to READY before moving on to the next repetition
                i=0
                while(malc.getDeviceState()!=DeviceState.READY):
                    time.sleep(1)
                    i+=1
                    if i>break_limit:
                        print "Timeout hit waiting for DeviceState to be READY"
                        # This point could get hit if the DeviceState went to FAILED rather than READY
                        # In this case we would still want to move to the next repeat rather than kill
                        # the scan, however if we wanted to kill the scan at this point we could use
                        # quit() instead of break
                        break
                time.sleep(5)
                print("Repetition " + str(r + 1) + " complete")
            except Exception as e:
                print(e)


        print("Run complete")
