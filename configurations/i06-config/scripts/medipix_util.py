from time import sleep
from gda.epics import CAClient


def restart_medipix():
    """
    Script to restart the medipix step by step. Useful to recover after medipix crashes.
    The script needs to stop and restart the medipix at specific points.
    """

    def _wait_for_input(msg, input_match):
        while str(input(msg)).strip() != str(input_match):
            print("Please enter '" + str(input_match) + "' to continue.")

    BASE_PV = "BL06I"
    DEXTER_PV = BASE_PV + "-EA-DEXTR-01:"
    IOC_PV = BASE_PV + "-EA-IOC-09:"
    DET_PV = BASE_PV + "-EA-DET-02:CAM:"

    _wait_for_input("-->> turn off the medipix camera (press blue button for 6 sec), type 1 and enter to continue\n", 1)

    ca = CAClient()

    #stop the BL06I-EA-IOC-09 soft IOC
    print("--> stopping the " + IOC_PV)
    ca.caput(IOC_PV + "STOP", 1)
    sleep(3)
    ca.caget(IOC_PV + "LOAD.SEVR")
    print("--> "+ IOC_PV + " stopped.")

    # stop the BL06I-EA-DEXTR-01
    print("--> stopping the " + DEXTER_PV)
    ca.caput(DEXTER_PV + "STOP",1)
    print("--> " + DEXTER_PV + " stopped")
    sleep(3)

    _wait_for_input("-->> turn ON the medipix camera (press blue button), type 1 and enter to continue\n", 1)
    print("--> waiting for the medipix to boot...")
    sleep(20)

    print("--> restarting the Dexter: please wait...")
    ca.caput(DEXTER_PV + "START", "1")
    print("--> waiting for the dexter to boot...")
    sleep(20)

    print("--> restarting the " + IOC_PV +" please wait...")
    ca.caput(IOC_PV + "START", "1")
    print("--> waiting for the " + IOC_PV + " to boot...")
    sleep(20)

    print("--> setting the medipix thresholds: please wait...")
    ca.caput(DET_PV + "ThresholdEnergy1", 80)
    sleep(3)

    ca.caput(DET_PV + "ThresholdEnergy0", 7)
    sleep(3)

    print("--> setting the medipix acquistion times: please wait...")
    ca.caput(DET_PV + "AcquireTime",0.1)
    sleep(0.5)
    ca.caput(DET_PV + "AcquirePeriod", 0.105)
    sleep(0.5)
    ca.caput(DET_PV + "QuadMerlinMode", "24 bit")
    sleep(0.5)
    ca.caput(DET_PV + "ImageMode", "Continuous")
    sleep(0.5)
    ca.caput(DET_PV + "Acquire", 1)

    print("--> medipix reboot complete.")
