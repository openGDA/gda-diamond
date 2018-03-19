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

def collectDarkFrame(expo=1):
    EXPOSURE.caputWait(expo)
#     sleep(2)
    ACQ_PERIOD.caputWait(expo+0.2)
#     sleep(2)
    BACKGROUND_ENABLE.caputWait(0)
#     sleep(2)
    ACQUIRE.caputWait(1)
    sleep(1)
    BACKGROUND_ENABLE.caputWait(1)
#     sleep(2)
    BACKGROUND_SAVE.caputWait(1)
    
