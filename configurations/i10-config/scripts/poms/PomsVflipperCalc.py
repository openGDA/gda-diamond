#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

# Taken from /dls/i06-1/scripts/POMS/PomsSocketDevice.py on 5-Jul-2012 (not
# under version control).




### Configure vflipperCalc using defaults

#print     repr(poms_default_vflipper_calc('vflipperCalc'))
#vflipperCalc = poms_default_vflipper_calc('vflipperCalc')
#print repr(vflipperCalc)

### Configure vflipperCalc manually
# from poms.PomsVflipperCalc import FlipperCalcDeviceClass
# #
# vflipperCalc = FlipperCalcDeviceClass('vflipperCalc', nameMagnet='vmag',
#         nameCounterTimerA='macr16',
#         nameCounterTimerB='macj18', 
#         nameCounterTimerC='macj19',
#         nameCounterTimerD='macj118', 
#         nameCounterTimerE='mac119',
#         nameCalc1='XMCD', calc1='B2/A2-B1/A1',
#         nameCalc2='X2',   calc2='B2/A2+B1/A1',
#         nameCalc3='XAS', calc3='X2/2.0',
#         nameCalc4='TDIF', calc4='C1/A1-C2/A2',
#         nameCalc5='X5',   calc5='C1/A1+C2/A2',
#         nameCalc6='TXAS', calc6='X5/2.0')
#        
#Note: For some reason the expression evaluation doesn't work with parentheses
#      at the moment, so you will have to rely on operator precedence and use
#      of output values as intermediate values as in the example above

#vflipperCalc = FlipperCalcDeviceClass('vflipperCalc', nameMagnet='vmag',
#        nameCounterTimerA='macr19',
#        nameCounterTimerB='macr16', nameCounterTimerC='mac117',
#        nameCounterTimerD='macj118', nameCounterTimerE='mac11',
#        nameCalc1='EDIF', calc1='B2/A2-B1/A1',
#        nameCalc2='X2',   calc2='B2/A2+B1/A1',
#        nameCalc3='EXAS', calc3='X2/2.0',
#        nameCalc4='TDIF', calc4='C1/A1-C2/A2',
#        nameCalc5='X5',   calc5='C1/A1+C2/A2',
#        nameCalc6='TXAS', calc6='X5/2.0')










from time import sleep
from gda.device.detector.etldetector import ETLDetector
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
and X1, X2, X3, X4, X5 & X6 are the calculated values.

To change the magnet scannable, call .setMagnet('magnet_name')
To change the counter timer scannables, call 
    .setCounters('nameCounterTimerA', 'nameCounterTimerB', 'nameCounterTimerC',
                 'nameCounterTimerD', 'nameCounterTimerE')
To change the calculations, call 
    .setCalcs('nameCalc1', 'calc1', 'nameCalc2', 'calc2', 'nameCalc3', 'calc3',
              'nameCalc4', 'calc4', 'nameCalc5', 'calc5', 'nameCalc6', 'calc6'):
    e.g.
    >>> vFlipper.getMagnet()
    >>> vFlipper.getCounters()
    >>> vFlipper.getCalcs()
    >>> vflipper.setMagnet('vmag')
    >>> vflipper.setCounters('macr119', 'macr120', 'macr121', 'macr122', 'macr123')
    >>> vflipper.setCalcs('EDIF', 'B2/A2-B1/A1', 'X2',   'B2/A2+B1/A1',
                          'EXAS', 'X2/2.0',
                          'TDIF', 'C1/A1-C2/A2', 'X5',   'C1/A1+C2/A2',
                          'TXAS', 'X5/2.0')
Note: For some reason the expression evaluation doesn't work with parentheses
      at the moment, so you will have to rely on operator precedence and use
      of output values as intermediate values as in the example above
"""
    def __init__(self, name, nameMagnet, nameCounterTimerA, nameCounterTimerB,
                       nameCounterTimerC, nameCounterTimerD, nameCounterTimerE,
                       nameCalc1, calc1, nameCalc2, calc2, nameCalc3, calc3,
                       nameCalc4, calc4, nameCalc5, calc5, nameCalc6, calc6):
        self.setName(name);
        self.setInputNames(['field', 'theta1', 'theta2', 'phi1', 'phi2',
                            'countTime', 'zeroRestTime']);
        #self.setExtraNames done in self.setCounters
        self.setOutputFormat(["%6.4f", "%6.3f", "%6.3f", "%6.3f", "%6.3f",
                              "%6.3f", "%6.3f"] + self.getExtraNameFormats());
        self.setLevel(7);
        self.setMagnet(nameMagnet)
        self.setCounters(nameCounterTimerA, nameCounterTimerB, nameCounterTimerC,
                         nameCounterTimerD, nameCounterTimerE, False)
        self.setCalcs(nameCalc1, calc1, nameCalc2, calc2, nameCalc3, calc3,
                      nameCalc4, calc4, nameCalc5, calc5, nameCalc6, calc6)
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
            "nameCalc3=%r, calc3=%r" + "nameCalc4=%r, calc4=%r" + \
            "nameCalc5=%r, calc5=%r" + "nameCalc6=%r, calc6=%r)"
        return format % (
            self.name, self.magnet.name, self.counterA.name, self.counterB.name,
            self.counterC.name, self.counterD.name, self.counterE.name,
            self.nameCalc1, self.calc1, self.nameCalc2, self.calc2,
            self.nameCalc3, self.calc3, self.nameCalc4, self.calc4,
            self.nameCalc5, self.calc5, self.nameCalc6, self.calc6)

    def getMagnet(self):
        print  'nameMagnet = %r' % self.nameMagnet
        return self.nameMagnet

    def setMagnet(self, nameMagnet):
        self.nameMagnet = nameMagnet
        self.magnet = vars(gdamain)[nameMagnet];
        return;

    def getCounters(self):
        print  'nameCounterTimerA = %r' % self.counterA.name, \
             ', nameCounterTimerB = %r' % self.counterB.name, \
             ', nameCounterTimerC = %r' % self.counterC.name, \
             ', nameCounterTimerD = %r' % self.counterD.name, \
             ', nameCounterTimerE = %r' % self.counterE.name
        return self.counterA.name, self.counterB.name, self.counterC.name, \
               self.counterD.name, self.counterE.name

    def setCounters(self, nameCounterTimerA, nameCounterTimerB,
                          nameCounterTimerC, nameCounterTimerD,
                          nameCounterTimerE, updateExtraNames=True):
        self.counterA = vars(gdamain)[nameCounterTimerA];
        self.counterB = vars(gdamain)[nameCounterTimerB];
        self.counterC = vars(gdamain)[nameCounterTimerC];
        self.counterD = vars(gdamain)[nameCounterTimerD];
        self.counterE = vars(gdamain)[nameCounterTimerE];
        assert isinstance(self.counterA, ETLDetector)
        assert isinstance(self.counterB, ETLDetector)
        assert isinstance(self.counterC, ETLDetector)
        assert isinstance(self.counterD, ETLDetector)
        assert isinstance(self.counterE, ETLDetector)
        if updateExtraNames:
            self.updateExtraNames()

    def getCalcs(self):
        print   'nameCalc1 = %r,' % self.nameCalc1, 'calc1 = %r,' % self.calc1, \
                'nameCalc2 = %r,' % self.nameCalc2, 'calc2 = %r,' % self.calc2, \
                'nameCalc3 = %r,' % self.nameCalc3, 'calc3 = %r,' % self.calc3, \
                'nameCalc4 = %r,' % self.nameCalc4, 'calc4 = %r,' % self.calc4, \
                'nameCalc5 = %r,' % self.nameCalc5, 'calc5 = %r,' % self.calc5, \
                'nameCalc6 = %r,' % self.nameCalc6, 'calc6 = %r'  % self.calc6
        return  self.nameCalc1, self.calc1, self.nameCalc2, self.calc2, \
                self.nameCalc3, self.calc3, self.nameCalc4, self.calc4, \
                self.nameCalc5, self.calc5, self.nameCalc6, self.calc6

    def setCalcs(self, nameCalc1, calc1, nameCalc2, calc2, nameCalc3, calc3,
                       nameCalc4, calc4, nameCalc5, calc5, nameCalc6, calc6,
                       updateExtraNames=True):
        self.nameCalc1, self.calc1 = nameCalc1, calc1
        self.nameCalc2, self.calc2 = nameCalc2, calc2
        self.nameCalc3, self.calc3 = nameCalc3, calc3
        self.nameCalc4, self.calc4 = nameCalc4, calc4
        self.nameCalc5, self.calc5 = nameCalc5, calc5
        self.nameCalc6, self.calc6 = nameCalc6, calc6
        if updateExtraNames:
            self.updateExtraNames()

    def updateExtraNames(self):
        self.setExtraNames(['A1'+self.counterA.name, 'A2'+self.counterA.name,
                            'B1'+self.counterB.name, 'B2'+self.counterB.name,
                            'C1'+self.counterC.name, 'C2'+self.counterC.name,
                            'D1'+self.counterD.name, 'D2'+self.counterD.name,
                            'E1'+self.counterE.name, 'E2'+self.counterE.name,
                            'X1'+self.nameCalc1, 'X2'+self.nameCalc2,
                            'X3'+self.nameCalc3, 'X4'+self.nameCalc4,
                            'X5'+self.nameCalc5, 'X6'+self.nameCalc6]);

    def getExtraNameFormats(self):
        return ["%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f",
                "%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f",
                "%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f",
                "%20.12f"]

    def getCounter(self):
        return self.counterA.name, self.counterB.name, self.counterC.name, self.counterD.name, self.counterE.name

    #PseudoDevice Implementation
    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": [field, theta1, theta2, phi1, phi2, countTime, zeroRestTime, countA1, countA2, countB1, countB2, countC1, countC2, countD1, countD2, countE1, countE2, X1, X2, X3, X4, X5, X6]: " + str(self.getPosition());
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
        try:
            X5 = eval(self.calc5)
        except ZeroDivisionError:
            X5 = float('NaN')
        try:
            X6 = eval(self.calc6)
        except ZeroDivisionError:
            X6 = float('NaN')
        
        return [self.field, self.theta1, self.theta2, self.phi1, self.phi2,
                self.countTime, self.zeroRestTime,
                self.count1[0], self.count2[0], self.count1[1], self.count2[1],
                self.count1[2], self.count2[2], self.count1[3], self.count2[3],
                self.count1[4], self.count2[4], X1, X2, X3, X4, X5, X6];
    
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

    def startCounterIfNecessary(self, counter, scalerNames):
        counter.setCollectionTime(self.countTime)
        counter.collectData()
        #if not counter.getScalerName() in scalerNames:
        #    print "Starting", counter.getScalerName(), "as it doesn't have the same scaler as another in", scalerNames
        #    scalerNames += counter.getScalerName()
        #else:
        #    print "Not starting", counter.getScalerName(), 'as it has the same scaler as another in', scalerNames

    def countOnce(self):
        self.counterA.setCollectionTime(self.countTime);
        self.counterA.collectData();
        scalerNames=[self.counterA.getScalerName()]
        
        self.startCounterIfNecessary(self.counterB, scalerNames)
        self.startCounterIfNecessary(self.counterC, scalerNames)
        self.startCounterIfNecessary(self.counterD, scalerNames)
        self.startCounterIfNecessary(self.counterE, scalerNames)
        while self.counterA.isBusy() or self.counterB.isBusy() or \
              self.counterC.isBusy() or self.counterD.isBusy() or \
              self.counterE.isBusy():
            sleep(0.1);

        return [self.counterA.getPosition(), self.counterB.getPosition(),
                self.counterC.getPosition(), self.counterD.getPosition(),
                self.counterE.getPosition()];

    def isBusy(self):
        sleep(1);
        return False;
