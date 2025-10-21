from collections import OrderedDict
from epics_scripts.pv_scannable_utils import caput
from time import sleep

def restart_ex():
    pv_times = OrderedDict([("BL07I-EA-IOC-32:RESTART", 2),
                            ("BL07I-ML-MALC-01:RESTART", 30),
                            ("BL07I-CS-EXC1-01:RESTART", 20)])
    restart_malcolm("Excalibur", pv_times)

def restart_ei():
    pv_times = OrderedDict([("BL07I-EA-IOC-32:RESTART", 2),
                            ("BL07I-ML-MALC-01:RESTART", 30),
                            ("BL07I-CS-EIG1-01:RESTART", 20)])
    restart_malcolm("Eiger", pv_times)

def restart_p2():
    pv_times = OrderedDict([("BL07I-EA-IOC-32:RESTART", 2),
                            ("BL07I-ML-MALC-01:RESTART", 30),
                            ("BL07I-EA-DET-02:RESTART", 75),
                            ("BL07I-EA-IOC-04:RESTART", 30)])
    restart_malcolm("Pilatus 2", pv_times)

def restart_p3():
    pv_times = OrderedDict([("BL07I-EA-IOC-34:RESTART", 2),
                            ("BL07I-ML-MALC-02:RESTART", 10),
                            ("BL07I-EA-DET-03:RESTART", 20),
                            ("BL07I-EA-IOC-06:RESTART", 30)])
    restart_malcolm("Pilatus 3", pv_times)

def restart_malcolm(detector_name, pv_times):

    def restart_ioc(restart_pv, time_to_wait):
        print("Restarting IOC " + restart_pv +" for " +str(time_to_wait) +"s")
        caput(restart_pv, 1)
        sleep(time_to_wait)
        caput(restart_pv, 0) #This just resets the button in the IOC window as some of them get stuck

    print("Restarting MALCOLM IOCs for detector " + detector_name +", this will take a couple of minutes.")
    for pv, time in pv_times.items():
        restart_ioc(pv, time)
    print("IOC restart complete.")