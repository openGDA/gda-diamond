# Scripts for running XANES scanning in dummy mode

import sys
import time

print("Running tomo_scan.py to define functions")

def run_tomo_scan(tomo_params, scan_request):
    try:
        run_tomo_scan_internal(tomo_params, scan_request)
        print("Tomography scan completed")
    except (KeyboardInterrupt):
        print("Tomography scan interrupted by user")
    except:
        print("Tomography scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_scan_internal(tomo_params, scan_request):
    print("Running tomography scan")
    print("tomo_params = {}".format(tomo_params))
    print("scan_request = {}".format(scan_request))
    time.sleep(5)

def run_tomo_dry_run(tomo_params, scan_request):
    try:
        run_tomo_dry_run_internal(tomo_params, scan_request)
        print("Tomography dry run completed")
    except (KeyboardInterrupt):
        print("Tomography dry run interrupted by user")
    except:
        print("Tomography dry run terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_dry_run_internal(tomo_params, scan_request):
    print("Running tomography dry run")
    print("tomo_params = {}".format(tomo_params))
    print("scan_request = {}".format(scan_request))
    time.sleep(5)
