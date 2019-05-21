# Dummy version of standards_scan function for testing purposes

import sys
from time import sleep

def standards_scan(*args):
    try:
        run_standards_scan(args)
    except (KeyboardInterrupt):
        print("Standards scan interrupted by user")
    except:
        print("Standards scan terminated abnormally: {0}".format(sys.exc_info()[0]))

def run_standards_scan(*args):
    print("Running standards scan with arguments: {}".format(args))
    sleep(5)
    print("Finished running standards scan")
