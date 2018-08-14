from gda.epics import CAClient
from time import sleep

BASE_PV = 'BL11J-EA-DET-02:'
CAM = 'CAM'
PROC = 'PROC:'

ACQUIRE = CAClient(BASE_PV + CAM + 'Acquire')
ACQUIRE.configure()
EXPOSURE = CAClient(BASE_PV + CAM + 'AcquireTime')
EXPOSURE.configure()
ACQ_PERIOD = CAClient(BASE_PV + CAM + 'AcquirePeriod')
ACQ_PERIOD.configure()
BACKGROUND_ENABLE = CAClient(BASE_PV + PROC + 'EnableBackground')
BACKGROUND_ENABLE.configure()
BACKGROUND_SAVE = CAClient(BASE_PV + PROC + 'SaveBackground')
BACKGROUND_SAVE.configure()

client = CAClient()
caputWait = client.caputWait

def collectDarkFrame(exposure=1.0):
    BACKGROUND_ENABLE.caputWait(0)
    scan(ds, 1, 1, 1, perkin_hdf, exposure)
    BACKGROUND_SAVE.caputWait(1)
    BACKGROUND_ENABLE.caput(1)
