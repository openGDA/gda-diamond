# Functions for running ptychography scanning in dummy mode
import sys
from time import sleep

def run_ptychography_scan_request(scanRequest):
    try:
        run_ptychography_scan(scanRequest)
    except (KeyboardInterrupt):
        print("Ptychography scan interrupted by user")
    except:
        print("Ptychography scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_ptychography_scan(scanRequest):
    print("Running ptychography scan with {}".format(scanRequest))
    sleep(2)
    print("Finished running ptychography scan")
