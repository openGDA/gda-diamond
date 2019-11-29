# Scripts for running XANES scanning in dummy mode

import sys
import time

print("Running tomo_scan.py to define functions")

def run_tomo_scan(scan_request, tomo_params):
    try:
        run_tomo_scan_internal(scan_request, tomo_params)
        print("Tomography scan completed")
    except (KeyboardInterrupt):
        print("Tomography scan interrupted by user")
    except:
        print("Tomography scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_scan_internal(scan_request, tomo_params):
    print("Running tomography scan\n")
    print("scan_request = {}\n".format(scan_request))
    print("tomo_params = {}\n".format(tomo_params))
    time.sleep(5)

def run_tomo_dry_run(scan_request, tomo_params):
    try:
        run_tomo_dry_run_internal(scan_request, tomo_params)
        print("Tomography dry run completed")
    except (KeyboardInterrupt):
        print("Tomography dry run interrupted by user")
    except:
        print("Tomography dry run terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_dry_run_internal(scan_request, tomo_params):
    print("Running tomography dry run")
    print("scan_request = {}\n".format(scan_request))
    print("tomo_params = {}\n".format(tomo_params))
    time.sleep(5)
