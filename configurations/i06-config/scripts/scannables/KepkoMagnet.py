from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from math import pow
from time import sleep

#connect the Kepko to Analogue output 2 in patch panel U2 (branchline)
#it calculates the field from the current with a polynomial
#the getPosition uses a inverted polynomial, but it does introduce an error of about 4 Oe 
#it should be replaced with a look-up table

class KepkoMagnet(ScannableMotionBase):
    def __init__(self, name, pv):
        self.setName(name);
        self.setInputNames(['Oersted'])
        self.setOutputFormat(['%5.0f'])
        self.setLevel(6)
        self.ch=CAClient(pv)
        self.ch.configure() 
        self.coeff=[0.0, 1.0]
        self.invCoeff=[0.0, 1.0]
        self.useInvCoeff=False
        self.fieldTolerance=10
        self.lastField = -999

    def setConvCoeff(self, coeff):
        self.coeff=coeff

    def setInvConvCoeff(self, invCoeff):
        self.invCoeff=invCoeff

    def calcCurrent(self, oersted):
        ampere=float(0.0)
        k=0.0
        for i in self.invCoeff:
            ampere+= i*pow(oersted, k)
            k+=1
        return ampere

    def getCurrent(self):
        return float(self.ch.caget())*0.4

    def calcField(self, ampere):
        oersted=float(0.0)
        k=0.0
        for i in self.coeff:
            oersted+= i*pow(ampere, k)
            k+=1
        if self.useInvCoeff:
            return oersted
        diff=abs(oersted-self.lastField)
        if diff > self.fieldTolerance:
            print "The last oersted value written (%r) differs from the oersted value (%r) calculated from the current (%r) by %r" % (
                self.lastField, oersted, ampere, diff)
            print "This is more than the warning tolerance (%r)" % self.fieldTolerance
        return self.lastField

    #scannable implementation

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        return self.calcField(self.getCurrent())

    def asynchronousMoveTo(self, newfield):
        self.lastField = newfield
        newcurrent = self.calcCurrent(newfield)
        self.ch.caput(newcurrent/0.4)
        sleep(0.5)
        return None

    def isBusy(self):
        return False 
 
# Initialise the scannable
#exec("magnet = None")
#print"-> connect the Kepko to Analogue output 2 in patch panel U2 (branchline)"
#print"-> magnet calibration for pole gap = 35.4 mm and bobbin turns = 784" 
#magnet = KepkoMagnet("magnet", "BL06J-EA-USER-01:AO2")
#
#magnet.setConvCoeff([0, 253.16, 7.22765, 9.37523, -1.81716, -3.49587, 0.155178, 0.267718, -0.00433883, -0.00662351])
#magnet.setInvConvCoeff([0, 0.00369277, -7.65554e-07, 6.49905e-09,5.76312e-12, -6.23302e-14, -1.77119e-17, 2.0429e-19,1.8207e-23, -1.70236e-25])