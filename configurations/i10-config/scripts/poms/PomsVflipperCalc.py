#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

# Taken from /dls/i06-1/scripts/POMS/PomsSocketDevice.py on 5-Jul-2012 (not
# under version control).

from time import sleep
from gda.device.scannable import PseudoDevice

import __main__ as gdamain

#The Class for creating a flipper based on the POMS magnet control 
class FlipperCalcDeviceClass(PseudoDevice):
    """This flips between two different field configurations in POMS, using the array
argument [field_Tesla, theta1_Deg, theta2_Deg, phi1_Deg, phi2_Deg, countTime_S,
          zeroRestTime_S]
    e.g.
    
    >>> pos vflipperCalc [0.1 0 180 180 0 1.5 0.5]

It returns 10 counter timer values (5 before and 5 after), plus several
configurable calculations.

where A1, B1, C1, D1 & E1 are the counts at the demanded field, theta1 and phi1.
  and A2, B2, C2, D2 & E2 are the counts at the demanded field, theta2 and phi2.
and X1, X2, X3 & X4 are the calculated values.

To change the magnet scannable, call .setMagnet('magnet_name')
To change the counter timer scannables, call 
    .setCounters('nameCounterTimerA', 'nameCounterTimerB', 'nameCounterTimerC',
                 'nameCounterTimerD', 'nameCounterTimerE')
To change the calculations, call 
    .setCalcs('nameCalc1', 'calc1', 'nameCalc2', 'calc2', 'nameCalc3', 'calc3',
              'nameCalc4', 'calc4'):
    e.g.
    >>> vflipper.setMagnet('vmag')
    >>> vflipper.setCounters('macr119', 'macr120', 'macr121', 'macr122', 'macr123')
    >>> vflipper.setCalcs('EDIF', 'B2/A2-B1/A1',
                          'Q2',   'B2/A2+B1/A1',
                          'EXAS', 'Q2/2.',
                          'Q4',   'C1/A1+C2/A2'))

Note: For some reason the expression evaluation doesn't work with parentheses
      at the moment, so you will have to rely on operator precedence and use
      of output values as intermediate values as in the example above
"""
    def __init__(self, name, nameMagnet, nameCounterTimerA, nameCounterTimerB,
                       nameCounterTimerC, nameCounterTimerD, nameCounterTimerE,
                       nameCalc1, calc1, nameCalc2, calc2,
                       nameCalc3, calc3, nameCalc4, calc4):
        self.setName(name);
        self.setInputNames(['field', 'theta1', 'theta2', 'phi1', 'phi2',
                            'countTime', 'zeroRestTime']);
        #self.setExtraNames done in self.setCounters
        self.setOutputFormat(["%6.4f", "%6.3f", "%6.3f", "%6.3f", "%6.3f",
                              "%6.3f", "%6.3f"] + self.getExtraNameFormats());
        self.setLevel(7);
        self.magnet = vars(gdamain)[nameMagnet];
        self.setCounters(nameCounterTimerA, nameCounterTimerB, nameCounterTimerC,
                         nameCounterTimerD, nameCounterTimerE, False)
        self.setCalcs(nameCalc1, calc1, nameCalc2, calc2,
                      nameCalc3, calc3, nameCalc4, calc4)
        self.field=0;
        self.theta1=0;
        self.phi1=0;
        self.theta2=0;
        self.phi2=360;
        self.countTime=1;
        self.zeroRestTime=1;
        self.count1=[0, 0, 0, 0, 0];
        self.count2=[0, 0, 0, 0, 0];
        self.verbose=False

    def __repr__(self):
        format = "FlipperDeviceClass(name=%r, nameMagnet=%r," + \
            "nameCounterTimerA=%r, nameCounterTimerB=%r, nameCounterTimerC=%r" + \
            "nameCounterTimerD=%r, nameCounterTimerE=%r" + \
            "nameCalc1=%r, calc1=%r" + "nameCalc2=%r, calc2=%r" + \
            "nameCalc3=%r, calc3=%r" + "nameCalc4=%r, calc4=%r)"
        return format % (
            self.name, self.magnet.name, self.counterA.name, self.counterB.name,
            self.counterC.name, self.counterD.name, self.counterE.name,
            self.nameCalc1, self.calc1, self.nameCalc2, self.calc2,
            self.nameCalc3, self.calc3, self.nameCalc4, self.calc4)

    def setMagnet(self, nameMagnet):
        self.magnet = vars(gdamain)[nameMagnet];
        return;

    def setCounters(self, nameCounterTimerA, nameCounterTimerB,
                          nameCounterTimerC, nameCounterTimerD,
                          nameCounterTimerE, updateExtraNames=True):
        self.counterA = vars(gdamain)[nameCounterTimerA];
        self.counterB = vars(gdamain)[nameCounterTimerB];
        self.counterC = vars(gdamain)[nameCounterTimerC];
        self.counterD = vars(gdamain)[nameCounterTimerD];
        self.counterE = vars(gdamain)[nameCounterTimerE];
        if updateExtraNames:
            self.updateExtraNames()

    def setCalcs(self, nameCalc1, calc1, nameCalc2, calc2, nameCalc3, calc3,
                       nameCalc4, calc4, updateExtraNames=True):
        self.nameCalc1, self.calc1 = nameCalc1, calc1
        self.nameCalc2, self.calc2 = nameCalc2, calc2
        self.nameCalc3, self.calc3 = nameCalc3, calc3
        self.nameCalc4, self.calc4 = nameCalc4, calc4
        if updateExtraNames:
            self.updateExtraNames()

    def updateExtraNames(self):
        self.setExtraNames(['A1'+self.counterA.name, 'A2'+self.counterA.name,
                            'B1'+self.counterB.name, 'B2'+self.counterB.name,
                            'C1'+self.counterC.name, 'C2'+self.counterC.name,
                            'D1'+self.counterD.name, 'D2'+self.counterD.name,
                            'E1'+self.counterE.name, 'E2'+self.counterE.name,
                            'X1'+self.nameCalc1, 'X2'+self.nameCalc2,
                            'X3'+self.nameCalc3, 'X4'+self.nameCalc4]);

    def getExtraNameFormats(self):
        return ["%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f",
                "%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f",
                "%20.12f", "%20.12f", "%20.12f", "%20.12f"]

    def getCounter(self):
        return self.counterA.name, self.counterB.name, self.counterC.name, self.counterD.name, self.counterE.name

    #PseudoDevice Implementation
    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": [field, theta1, theta2, phi1, phi2, countTime, zeroRestTime, countA1, countA2, countB1, countB2, countC1, countC2, countD1, countD2, countE1, countE2, X1, X2. X3,. X4]: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        A1, B1, C1, D1, E1 = float(self.count1[0]), float(self.count1[1]), float(self.count1[2]), float(self.count1[3]), float(self.count1[4])
        A2, B2, C2, D2, E2 = float(self.count2[0]), float(self.count2[1]), float(self.count2[2]), float(self.count2[3]), float(self.count2[4])
        try:
            X1 = eval(self.calc1)
        except ZeroDivisionError:
            X1 = float('NaN')
        try:
            X2 = eval(self.calc2)
        except ZeroDivisionError:
            X2 = float('NaN')
        try:
            X3 = eval(self.calc3)
        except ZeroDivisionError:
            X3 = float('NaN')
        try:
            X4 = eval(self.calc4)
        except ZeroDivisionError:
            X4 = float('NaN')
        
        return [self.field, self.theta1, self.theta2, self.phi1, self.phi2,
                self.countTime, self.zeroRestTime,
                self.count1[0], self.count2[0], self.count1[1], self.count2[1],
                self.count1[2], self.count2[2], self.count1[3], self.count2[3],
                self.count1[4], self.count2[4], X1, X2, X3, X4];
    
    def asynchronousMoveTo(self,newPos):
        self.field=newPos[0];
        self.theta1=newPos[1];
        self.theta2=newPos[2];
        self.phi1=newPos[3];
        self.phi2=newPos[4];
        self.countTime=newPos[5];
        self.zeroRestTime=newPos[6];
        
        self.magnet.moveTo([self.field, self.theta1, self.phi1]);
        self.count1=self.countOnce();
        
        if self.verbose:
            print 'zero rest for ' + str(self.zeroRestTime) + ' seconds ...';
        
        self.magnet.moveTo([0,0,0]);
        sleep(self.zeroRestTime);
        self.magnet.moveTo([self.field, self.theta2, self.phi2]);
        self.count2=self.countOnce();
        
        self.magnet.moveTo([0,0,0]);
        return;
    
    def countOnce(self):
        self.counterA.setCollectionTime(self.countTime);
        self.counterA.collectData();
        while self.counterA.isBusy():
            sleep(0.1);

        return [self.counterA.getPosition(), self.counterB.getPosition(),
                self.counterC.getPosition(), self.counterD.getPosition(),
                self.counterE.getPosition()];

    def isBusy(self):
        sleep(1);
        return False;
