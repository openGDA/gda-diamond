# Functions to control the IOC
import time

from gda.epics import CAClient
from i08_shared_utilities import is_live


def restart_ioc():
    if is_live():
        print('Restarting the IOC')
        caClient = CAClient()
        try:
            caClient.configure()
            caClient.caput('BL08I-CS-RSTRT-01:PSC:RESTART', 1, 0)
        finally:
            caClient.clearup()
    else:
        print('Restarting the IOC (dummy mode)')
        time.sleep(2)

    print('IOC restarted')
