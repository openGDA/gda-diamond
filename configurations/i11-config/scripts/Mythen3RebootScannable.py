import time
import os
from datetime import datetime
from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caput, caget
"""

Usage:

Use this CMS as a scannable if you are worried there might be a module loss issues on the mythen3

Example usage:


cms1 = CMS() < this currently happens automatically at gda startup

scan delta 1 2 0.5 mythen_nx 1 cms1

###############

You can also run this script directly to just reboot the mythen3

###############

"""


def caput_and_ensure(PV, value, max_tries=100):

    caput(PV, value)

    tries = 0

    while (int(caget(PV)) != value) and (tries < max_tries):
        time.sleep(0.2)

        if tries%20 == 0:
            caput(PV, value)
        
        tries = tries+1


class CMS(ScannableMotionBase):

    """

    CMS = Check Mythen3 Status

    """


    def __init__(self, name="CMS", n_modules=28):

        self.name = name #not sure if this is needed?
        self.n_modules = n_modules
        self.mythen3_config = "/dls_sw/i11/software/mythen3/diamond/mythen3.config"

        self.time_now = datetime.now()
        self.year = str(self.time_now.year)

        self.path = os.path.join('/dls/i11/data',self.year)
        self.commissioning_visits = [f for f in os.listdir(self.path) if "cm" in f]
        self.commissioning_visits.sort()
        self.current_visit = self.commissioning_visits[-1]
        self.current_visit_path =  os.path.join('/dls/i11/data',self.year,self.current_visit) 
        self.fh = os.path.join(self.current_visit_path,'processing/PSD_Health.log')

        print("cms1 log:",self.fh)

        self.enabled_modules = self.read_config(self.mythen3_config)
        self._stop = False

    def stop(self):
        # self._stop = True
        quit()

    def atPointStart(self):

        isHealthy = self.reboot_if_unhealthy()

        return 1


    def reboot_if_unhealthy(self):

        self.enabled_modules = self.read_config(self.mythen3_config)
        isMythenHealthy = self.isMythenHealthyCheck()

        if isMythenHealthy:
            #not busy so continue
            print(self.time_now_str(),"Mythen3 is healthy")
            #Return not busy. busy = False
            return True

        if not isMythenHealthy:
            print(self.time_now_str(),"MYTHEN3 IS UNHEALTHY!!")
            for i in range(10): #change this to make loops longer
                isMythenHealthy = self.isMythenHealthyCheck()
                time.sleep(1)
                print(self.time_now_str(),"Checking to see if it has recovered..")
                if isMythenHealthy:
                    return False

            active_modules = self.check_modules()
            unhealthy_modules = [n_mod+1 for n_mod in self.enabled_modules if n_mod not in active_modules]
            print(self.time_now_str(),"The following modules are not healthy:")
            print(unhealthy_modules, "(Counting from 1)")
            self.reboot_mythen(write_reset=True)
            self.resethdfwriter()
            ######## maybe just return False after reboot?
            #Return busy. busy = True
            return False


    def isBusy(self):

        return


    def getPosition(self):


        active_modules = self.check_modules()
        print("active modules:",active_modules)
        # self.isBusy(reset_hdf=False)

        return 1

    def asynchronousMoveTo(self, newPosition):
        """ we are not moveable """
        return 0


    def time_now_str(self):
        time_now_str = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        return time_now_str


    def read_config(self, mythen3_config_dir):

        """
        reads the config file and works out what modules are currently active

        """

        enabled_modules_hostnames = None

        with open(mythen3_config_dir) as file:
          lines = [line.rstrip() for line in file]

        for n,line in enumerate(lines):
            if line.startswith('hostname'):
                      enabled_modules_hostnames = line.split()[1::]

        enabled_modules = [int(n_mod.rstrip()[-3::])-100 for n_mod in enabled_modules_hostnames]

        return enabled_modules


    def check_modules(self):

        active_modules = [n_mod for n_mod in self.enabled_modules if (int(caget("BL11I-DI-PSD-01:Module{:02}Connected_RBV".format(n_mod+1))) == 2) ]

        return active_modules

    def isMythenHealthyCheck(self, checkstate=True):
        active_modules = self.check_modules()

        if checkstate:
            DetectorState = int(caget("BL11I-EA-DET-07:DET:DetectorState_RBV")) #1 = Error
        else:
            DetectorState = 2

        isMythenHealthyBool = (len(self.enabled_modules) == len(active_modules)) and (len(active_modules) != 0) and (DetectorState != 1)

        return isMythenHealthyBool

    def resethdfwriter(self):
        print("resethdfwriter")
        caput_and_ensure("BL11I-EA-DET-07:HDF:FileWriteMode", 2) #set hdf to stream
        caput_and_ensure("BL11I-EA-DET-07:HDF:Capture", 1) #set hdf to acquire
        # caput("BL11I-EA-DET-07:DET:Acquire", 1)
        # time.sleep(5)
        # acquiretime = caget('BL11I-EA-DET-07:DET:AcquireTime')
        # time.sleep(int(acquiretime))


    def MythenIOCStartandCheck(self):

        print(self.time_now_str(),"BL11I-EA-DET-07 IOC is about to be restarted (5ish mins)")
        caput('BL11I-EA-IOC-07:START',1)
        time.sleep(90)

        Mythen3IOCHealthy = False
        while not Mythen3IOCHealthy:
            try:
                Mythen3IOCModel = caget("BL11I-EA-DET-07:DET:Model_RBV")
                Mythen3IOCHealthy = (Mythen3IOCModel == "Mythen3")
            except:
                time.sleep(10)
                continue

            if Mythen3IOCHealthy:
                return

            elif Mythen3IOCModel == "Unknown":

                for i in range(10):

                    Mythen3IOCModel = caget("BL11I-EA-DET-07:DET:Model_RBV")
                    Mythen3IOCHealthy = (Mythen3IOCModel == "Mythen3")

                    if not Mythen3IOCHealthy:
                        print(self.time_now_str(),"Mythen3 IOC is in Unknown state. Checking to see if it configures properly..")
                        time.sleep(5)
                    elif Mythen3IOCHealthy:
                        return

                print(self.time_now_str(),"Mythen IOC failed to start properly. Turning off again (30 secs)")
                caput('BL11I-EA-IOC-07:STOP',1)
                time.sleep(30)
                self.MythenIOCStartandCheck()

    def write_bad_modules_to_log(self):

        print("Saving bad modules to log file:", self.fh)

        reset_date = datetime.now()

        with open(self.fh, 'a') as file:
            line = 'PSD reset on '+str(reset_date) + '\n'
            file.write(line)
            file.flush()
            file.close()

        with open(self.fh, 'a') as file:
            line = 'Modules and status after reboot' + '\n'
            file.write(line)
            file.flush()
            file.close()

        for n_mod in range(0, 28, 1):
            j = "BL11I-DI-PSD-01:Module{:02}Connected_RBV".format(n_mod+1)
            h = caget(j)
            with open(self.fh, 'a') as file:
                line = 'Module ' + str(j) + ' Status ' + str(h)  + '\n'
                file.write(line)
                file.flush()
                file.close()



    def reboot_mythen(self, write_reset=False):
        print(self.time_now_str(),'Mythen Reboot started')
        print("Will take approx 15 minutes")

        if write_reset:
            self.write_bad_modules_to_log()

        #IOCs off
        caput( 'BL11I-EA-MYTHN-01:STOP',1)
        caput( 'BL11I-EA-IOC-07:STOP',1)
        #caput( 'BL11I-EA-PRCO-01:STOP',1)
        print(self.time_now_str(),"IOC have been turned off")
        #PSD off
        caput( 'BL11I-DI-PSD-01:PSD:OFF',1)
        caput( 'BL11I-DI-PSD-01:PSD:OFF',0)
        print(self.time_now_str(),"BL11I-DI-PSD-01:PSD is now off. Waiting for full shutdown (2 mins)")
        time.sleep(120)


        #PSD on
        print(self.time_now_str(),"PSD is about to be turned back on (6ish mins)")
        caput('BL11I-DI-PSD-01:PSD:ON',1)
        caput('BL11I-DI-PSD-01:PSD:ON',0)

        time.sleep(45)

        isMythenHealthy = False
        while not isMythenHealthy:
            try:
                isMythenHealthy = self.isMythenHealthyCheck(checkstate=False)
                print("Waiting for modules to all turn on...")
                time.sleep(5)
            except:
                continue

        print(self.time_now_str(),"PSD is now on")

        #IOCs on
        print(self.time_now_str(),"BL11I-EA-MYTHN-01 IOC is about to be turned on (45 sec)")
        caput( 'BL11I-EA-MYTHN-01:START',1)
        time.sleep(45)
        print(self.time_now_str(),"BL11I-EA-MYTHN-01 IOC is now back on")


        self.MythenIOCStartandCheck()
        print(self.time_now_str(),"BL11I-EA-DET-07 IOC is now back on")
        #print("PRCO IOC is about to be turned on (3 mins)")

        #caput( 'BL11I-EA-PRCO-01:START',1)
        #time.sleep(180)
        #print("PRCO IOC is now back on")

        print(self.time_now_str(),"Setting energy and threshold...")
        #set PSD energy and threshold
        caput_and_ensure('BL11I-EA-DET-07:DET:BeamEnergy', 15000)
        caput_and_ensure('BL11I-EA-DET-07:DET:Counter1Threshold', 7500)
        caput_and_ensure('BL11I-EA-DET-07:DET:Counter2Threshold', 20000)
        caput_and_ensure('BL11I-EA-DET-07:DET:Counter3Threshold', 20000)

        self.write_bad_modules_to_log()
        print(self.time_now_str(),"Mythen Reboot Complete")


if __name__ == "__main__":

    cms1 = CMS()
    cms1.reboot_mythen()
