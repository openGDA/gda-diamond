"""
Scannable for converting Field in mT into eggcup magnet position in mm

David Burn

from rasor.scannable.eggcupMagnetsScannable import eggcupMagnetsScannable
#field = eggcupMagnetsScannable("Field", emecy1, emecy2, 177.0, 8.16, 18.1) # calibration for big magnets
#field = eggcupMagnetsScannable("field", emecy1, emecy2, 28.58, 9.06, 3.66) # calibration for medium magnets

        #self.calibration = [-8.16, 177.0, 18.1]   # for big magnets 
        #self.calibration = [-6.8507, 331.67598, 47.64438]   # for medium magnets 
        #self.calibration = [-6.54058, 10.32319, 2.69]   # for tiny magnets
"""
from gda.device.scannable import ScannableBase
from gda.epics import CAClient
import math
import time

class eggcupMagnetsScannable(ScannableBase):
    def __init__(self,name, emecy1, emecy2, A, t, y0):
        self.name=name
        self.setInputNames([name])
        self.setExtraNames(["emecy1", "emecy2"]);
        self.iambusy = 0
        self.currentPosition = 0
        
        self.emecy1 = emecy1
        self.emecy2 = emecy2

        self.calibration = [-t, A, y0]


    def rawGetPosition(self):
        self.currentPosition = self.emecy2()
        return [self.position2field(self.currentPosition), self.emecy1(), self.emecy2()]



    def rawAsynchronousMoveTo(self, field):
        #move both magnets, return when both magnets are in new position.
        self.iambusy = 1
        self.currentPosition = self.field2position(field)
        self.emecy1.a(-self.currentPosition)
        self.emecy2.a(self.currentPosition)
        self.emecy1.waitWhileBusy()
        self.emecy2.waitWhileBusy()
        self.iambusy = 0
    
    
    def field2position(self,field):
        # H = A x e(x/t)    exponential decay
        # -t1, A1, y0
        position = self.calibration[0]*math.log((field - self.calibration[2])/self.calibration[1]) 
        return position
    
    def position2field(self,position):
        field = self.calibration[1]*math.exp(position/self.calibration[0]) + self.calibration[2]
        return field
    
    def isBusy(self):
        return self.iambusy



""" ############################################################################### """
""" ############################################################################### """
""" ############################################################################### """

def homeMagnets():
    import datetime
    ca = CAClient();
    restTime = 0
    attempts = 0
    
    time_before = int(time.time())
    y1_before = float(caget("ME01D-EA-EMEC-01:Y1.VAL"))
    y2_before = float(caget("ME01D-EA-EMEC-01:Y2.VAL"))

    try:
        #ME01D-EA-EMEC-01:Y2.SEVR == "MAJOR" when on limit, == "NO_ALARM" when ok
        # SEVR = 0: no errors
        while (int(ca.caget("ME01D-EA-EMEC-01:Y1.SEVR")) == 0 or int(ca.caget("ME01D-EA-EMEC-01:Y2.SEVR")) == 0):
            attempts = attempts + 1
            
            # rest the motors then try a bit more
            if (attempts > 4):
                print "resting magnet motors for %d seconds" % restTime
                time.sleep(restTime)
                restTime = restTime + 30
                
            if (attempts > 6):
                print "Try reversing the direction"
                ca.caput("ME01D-EA-EMEC-01:Y1.VAL", float(caget("ME01D-EA-EMEC-01:Y1.VAL"))+0.5)
                ca.caput("ME01D-EA-EMEC-01:Y2.VAL", float(caget("ME01D-EA-EMEC-01:Y2.VAL"))-0.5)
                
                while (int(ca.caget("ME01D-EA-EMEC-01:Y1.DMOV")) == 0 or int(ca.caget("ME01D-EA-EMEC-01:Y2.DMOV")) == 0):
                    # wait while motor is moving
                    time.sleep(1)

            ca.caput("ME01D-EA-EMEC-01:Y1.LLM", float(caget("ME01D-EA-EMEC-01:Y1.VAL"))-10) # move the soft limits
            ca.caput("ME01D-EA-EMEC-01:Y2.HLM", float(caget("ME01D-EA-EMEC-01:Y2.VAL"))+10)

            ca.caput("ME01D-EA-EMEC-01:Y1.VAL", float(caget("ME01D-EA-EMEC-01:Y1.VAL"))-5)
            ca.caput("ME01D-EA-EMEC-01:Y2.VAL", float(caget("ME01D-EA-EMEC-01:Y2.VAL"))+5)

            print "waiting for magnet move"
            # DMOV = 0: moving ok, DMOV = 1: at limit, or stopped ok
            while (int(ca.caget("ME01D-EA-EMEC-01:Y1.DMOV")) == 0 or int(ca.caget("ME01D-EA-EMEC-01:Y2.DMOV")) == 0):
                # wait while motor is moving
                time.sleep(1)

    except:
        print "exception"

    time_after = int(time.time())
    y1_after = float(caget("ME01D-EA-EMEC-01:Y1.VAL"))
    y2_after = float(caget("ME01D-EA-EMEC-01:Y2.VAL"))


    """ saves log """
    f=open("/dls_sw/i10/scripts/beamline/logs/eggcup_motors.dat", 'a')
    timeStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    line = "%s\t%d\t%3.3f\t%3.3f\t%3.3f\t%3.3f \n" % (timeStr, (time_after - time_before), y1_before, y2_before, abs(y1_after)-20, abs(y2_after)-20 )
    f.write(line); f.flush(); f.close()



    time.sleep(5)

    ca.caput("ME01D-EA-EMEC-01:Y1.HOMF", 1)             #home magnet
    ca.caput("ME01D-EA-EMEC-01:Y1.OFF", -20.0)          #set user offset to -20
    
    ca.caput("ME01D-EA-EMEC-01:Y2.HOMR", 1)             #home magnet
    ca.caput("ME01D-EA-EMEC-01:Y2.OFF", 20.0)           #set user offset to 20
    
    ca.caput("ME01D-EA-EMEC-01:Y1.LLM", -50)            # set the soft limits
    ca.caput("ME01D-EA-EMEC-01:Y1.HLM", 50)
    ca.caput("ME01D-EA-EMEC-01:Y2.LLM", -50) 
    ca.caput("ME01D-EA-EMEC-01:Y2.HLM", 50)
            
            
    print "Eggcup magnet motors now homed"
    
""" ############################################################################### """
""" ############################################################################### """
""" ############################################################################### """

