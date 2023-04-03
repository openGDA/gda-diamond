import sys
import time

print("Running tomo_scan.py to define functions")

def run_tomo_scan(scanRequest, tomoParams):
    try:
        print("Running tomography scan")
        print("scanRequest = {}".format(scanRequest))
        print("tomoParams = {}".format(tomoParams))
        time.sleep(5)
        print("Tomography scan completed")
    except (KeyboardInterrupt):
        print("Tomography scan interrupted by user")
    except:
        print("Tomography scan terminated abnormally: {}".format(sys.exc_info()[0]))

def run_tomo_dry_run(scanRequest, tomoParams):
    try:
        print("Running tomography scan")
        print("scanRequest = {}".format(scanRequest))
        print("tomoParams = {}".format(tomoParams))
        time.sleep(5)
        print("Tomography dry run completed")
    except (KeyboardInterrupt):
        print("Tomography dry run interrupted by user")
    except:
        print("Tomography dry run terminated abnormally: {}".format(sys.exc_info()[0]))
