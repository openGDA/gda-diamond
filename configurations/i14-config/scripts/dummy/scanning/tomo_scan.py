# Scripts for running XANES scanning in dummy mode

import sys
import time

print("Running tomo_scan.py to define functions")

def run_tomo_scan(scanRequest, tomoParams):
    try:
        run_tomo_scan_internal(scanRequest, tomoParams)
        print("Tomography scan completed")
    except (KeyboardInterrupt):
        print("Tomography scan interrupted by user")
    except:
        print("Tomography scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_scan_internal(scanRequest, tomoParams):
    print("Running tomography scan")
    print("scanRequest = {}".format(scanRequest))
    print("tomoParams = {}".format(tomoParams))
    time.sleep(5)

def run_tomo_dry_run(scanRequest, tomoParams):
    try:
        run_tomo_dry_run_internal(scanRequest, tomoParams)
        print("Tomography dry run completed")
    except (KeyboardInterrupt):
        print("Tomography dry run interrupted by user")
    except:
        print("Tomography dry run terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_dry_run_internal(scanRequest, tomoParams):
    print("Running tomography dry run")
    print("scanRequest = {}".format(scanRequest))
    print("tomoParams = {}".format(tomoParams))
    time.sleep(5)
