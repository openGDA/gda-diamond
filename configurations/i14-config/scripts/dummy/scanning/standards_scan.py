# Dummy version of standards_scan function for testing purposes

import sys
from time import sleep

def standards_scan(energy_ranges, exposure_time, reverse_scan):
    try:
        run_standards_scan(energy_ranges, exposure_time, reverse_scan)
    except (KeyboardInterrupt):
        print("Standards scan interrupted by user")
    except:
        print("Standards scan terminated abnormally: {0}".format(sys.exc_info()[0]))

def run_standards_scan(energy_ranges, exposure_time, reverse_scan):
    print("Running standards scan")
    print("Energy_ranges: {}".format(energy_ranges))
    print("Exposure time: {}".format(exposure_time))
    print("Reverse scan: {}".format(str(reverse_scan)))
    sleep(5)
    print("Finished running standards scan")
