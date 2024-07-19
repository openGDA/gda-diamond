from gda.device.scannable import ScannableBase
from pd_epics import DisplayEpicsPVClass
from gda.epics import CAClient
from time import sleep
from gda.device import DeviceException

DEFAULT_RELATIVE_LOWER_TEMP = 10.0

class PhasePlateTempMonitor(ScannableBase):
    '''
    Scannable which checks the temperature of the phase plate motors at scan start and if any are over will wait until they have cooled to a suitable
    temperature before starting the scan.  Once the scan has started it will not check them again, leaving further overheating protection to the EPICS
    layer.
    '''

    motors=list()

    def __init__(self, name):
        self.setName(name)
        self.setInputNames(["SafeToMovePhasePlate"])
        self.setOutputFormat(['%s'])

    def getPosition(self):
        for motor in self.motors :
            if motor.isOverTemperature() :
                return False
        return True

    def isBusy(self):
        return False;

    def addMotor(self, motor):
        self.motors.append(motor)

    def atScanStart(self):
        for motor in (x for x in self.motors if x.isOverTemperature() ) :
            motor.waitUntilCool()

    def atPointStart(self):
        for motor in self.motors :
            motor.checkError()

    def asynchronousMoveTo(self, newpos):
        raise NotImplementedError("Read only scannable")

class MotorTempMonitor(DisplayEpicsPVClass):
    '''
    DisplayEpicsPVClass for the phase plate motor temperature monitors.  Provides access to the error (max) temperature pv and methods to check motor
    is at a safe temperature.
    '''

    def __init__(self, name, pvbase, unitstring, formatstring, relative_lower_temp=DEFAULT_RELATIVE_LOWER_TEMP):#PVbase e.g. BL16I-OP-PPR-01:S1:THETA
        DisplayEpicsPVClass.__init__(self, name, pvbase + ":TEMP", unitstring, formatstring)
        self.warning_client=CAClient( pvbase + ":TEMP:HIGH")
        self.warning_client.configure()
        self.error_client=CAClient( pvbase + ":TEMP:HIHI")
        self.error_client.configure()
        self.relative_lower_temp=relative_lower_temp

    def checkError(self):
        if self.getPosition() > float(self.error_client.caget()) :
            raise DeviceException("Motor " + self.name + " has overheated!")

    def isOverTemperature(self):
        return self.getPosition() > float(self.warning_client.caget())

    def waitUntilCool(self):
        counter = 0
        while self.getPosition() > (float(self.warning_client.caget()) - self.relative_lower_temp) :
            if(counter % 30 == 0) :
                print "Waiting for motor " + self.name + " to cool to a safe temperature to start the scan."
            counter+=1
            sleep(1)
