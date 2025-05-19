from gdascripts.utils import caput, caget
import time
from datetime import datetime
from gda.device.scannable import ScannableMotionBase

"""

Usage:

Use this CMS as a scannable if you are worried there might be a module loss issues on the mythen3

Example usage:

cms = CMS()

scan delta 1 2 0.5 mythen_nx 1 cms


"""

class CMS(ScannableMotionBase):

    """

    CMS = Check Mythen3 Status

    """


    def __init__(self, name="CMS", n_modules=None):

        self.name = name #not sure if this is needed?
        self.n_modules = n_modules
        self.mythen3_config = "/dls_sw/i11/software/mythen3/diamond/mythen3.config"
        self.fh = '/dls/i11/data/2025/cm40625-1/processing/PSD_Health.log'

        if self.n_modules == None:
            self.enabled_modules = self.read_config(self.mythen3_config)
        else:
            self.enabled_modules = range(self.n_modules)

    def stop(self):
        return

    def isBusy(self):

        active_modules = self.check_modules()
        isMythenHealthy = len(self.enabled_modules) == len(active_modules)

        if isMythenHealthy:
            #not busy so continue
            print("Mythen3 is healthy")
            #Return not busy. busy = False
            return False

        if not isMythenHealthy:

            c = 0

            while (self.check_modules() != len(self.enabled_modules) ):
                time.sleep(1)
                if c == 20:
                    break

            unhealthy_modules = [n_mod for n_mod in self.enabled_modules if n_mod not in active_modules]
            print("The following modules are not healthy:")
            print(unhealthy_modules)
            # original_filenumber = int(caget("BL11I-EA-DET-07:HDF:FileNumber_RBV"))
            self.rebootMythen3()
            self.resethdfwriter()
            ######## maybe just return False after reboot?
            #Return busy. busy = True
            return True

        return False


    def getPosition(self):
        active_modules = self.check_modules()

        print("active modules:",active_modules)

        return 1

    def asynchronousMoveTo(self, newPosition):
        """ we are not moveable """
        return 0


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


    def resethdfwriter(self):

        caput("BL11I-EA-DET-07:HDF:FileWriteMode", 2) #set hdf to stream
        caput("BL11I-EA-DET-07:HDF:Capture", 1) #set hdf to acquire
        # caput("BL11I-EA-DET-07:HDF:FileNumber", original_filenumber)
        # caput("BL11I-EA-DET-07:DET:Acquire", 1)


    def rebootMythen3(self):

        print('Mythen Reboot started')
        print("Will take approx 12 minutes")

        reset_date = datetime.now()

        with open(self.fh, 'a') as file:
            line = 'PSD reset on '+str(reset_date) + '\n'
            file.write(line)
            file.flush()
            file.close()

        with open(self.fh, 'a') as file:
            line = 'Modules and status before reboot' + '\n'
            file.write(line)
            file.flush()
            file.close()

        for i in range(1, 29, 1):
            if i < 10:
                j = 'BL11I-DI-PSD-01:Module0'+str(i)+'Connected_RBV'
                h = caget(j)
                with open(self.fh, 'a') as file:
                    line = 'Module ' + str(j) + ' Status ' + str(h)  + '\n'
                    file.write(line)
                    file.flush()
                    file.close()
            else:
                j = 'BL11I-DI-PSD-01:Module'+str(i)+'Connected_RBV'
                h = caget(j)
                with open(self.fh, 'a') as file:
                    line = 'Module ' + str(j) + ' Status ' + str(h)  + '\n'
                    file.write(line)
                    file.flush()
                    file.close()

        #IOCs off
        caput( 'BL11I-EA-MYTHN-01:STOP',1)
        caput( 'BL11I-EA-IOC-07:STOP',1)
        caput( 'BL11I-EA-PRCO-01:STOP',1)
        print("IOC have been turned off")


        #PSD off
        print("PSD is about to be turned off (2 mins)")
        caput( 'BL11I-DI-PSD-01:PSD:OFF',1)
        caput( 'BL11I-DI-PSD-01:PSD:OFF',0)
        time.sleep(120)
        print("PSD is now off")


        #PSD on
        print("PSD is about to be turned back on (6 mins)")
        caput( 'BL11I-DI-PSD-01:PSD:ON',1)
        caput( 'BL11I-DI-PSD-01:PSD:ON',0)
        time.sleep(360)
        print("PSD is now on")


        #IOCs on
        print("Mythen IOC is about to be turned on (45 sec)")
        caput( 'BL11I-EA-MYTHN-01:START',1)
        time.sleep(45)
        print("Mythen IOC is now back on")

        caput( 'BL11I-EA-IOC-07:START',1)
        time.sleep(10)
        print("EA IOC is now back on")

        print("PRCO IOC is about to be turned on (3 mins)")
        caput( 'BL11I-EA-PRCO-01:START',1)
        time.sleep(180)
        print("PRCO IOC is now back on")

        print("Setting energy and threshold...")
        #set PSD energy and threshold
        caput('BL11I-EA-DET-07:DET:BeamEnergy', 15000)
        caput('BL11I-EA-DET-07:DET:Counter1Threshold', 7500)


        with open(self.fh, 'a') as file:
            line = 'Modules and status after reboot' + '\n'
            file.write(line)
            file.flush()
            file.close()

        for i in range(1, 29, 1):
            if i < 10:
                j = 'BL11I-DI-PSD-01:Module0'+str(i)+'Connected_RBV'
                h = caget(j)
                with open(self.fh, 'a') as file:
                    line = 'Module ' + str(j) + ' Status ' + str(h)  + '\n'
                    file.write(line)
                    file.flush()
                    file.close()
            else:
                j = 'BL11I-DI-PSD-01:Module'+str(i)+'Connected_RBV'
                h = caget(j)
                with open(self.fh, 'a') as file:
                    line = 'Module ' + str(j) + ' Status ' + str(h)  + '\n'
                    file.write(line)
                    file.flush()
                    file.close()


        print('Mythen Reboot Complete')
