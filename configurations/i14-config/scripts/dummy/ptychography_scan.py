# Functions for running ptychography scanning in dummy mode
import sys
from time import sleep

def run_ptychography_scan_request(scanRequest, ptychoParams):
    try:
        run_ptychography_scan_request_internal(scanRequest, ptychoParams)
    except (KeyboardInterrupt):
        print("Ptychography scan interrupted by user")
    except:
        print("Ptychography scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_ptychography_scan_request_internal(scanRequest, ptychoParams):
    print("Running ptychography scan with ScanRequest {} and PtychographyParams {}".format(scanRequest, ptychoParams))
    sleep(2)
    print("Finished running ptychography scan")
