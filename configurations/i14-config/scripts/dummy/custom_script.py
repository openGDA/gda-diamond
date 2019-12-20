# Dummy custom script for testing purposes

import sys
import json
from time import sleep

def run_custom_script(params):
    params_obj = json.loads(params)
    print("Running custom script with {} parameter(s): {}".format(len(params_obj), params_obj))
    sleep(5)
    print("Finished running custom script")

try:
    run_custom_script(customParams)
except (KeyboardInterrupt):
    print("Custom script interrupted by user")
except:
    print("Custom script terminated abnormally: {0}".format(sys.exc_info()[0]))
