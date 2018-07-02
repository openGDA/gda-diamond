#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

# Taken from /dls/i06-1/scripts/POMS/PomsSocketDevice.py on 5-Jul-2012 (not
# under version control).






"""############################################################################
example to select the flipper to use
###############################################################################"""

#print repr(poms_default_vflipper('vflipper'))
#vflipper = poms_default_vflipper('vflipper')
#print repr(vflipper)

### Configure vflipper manually
#from poms.PomsVflipper import FlipperDeviceClass
#from David.scannables.PomsVflipper import FlipperDeviceClass

#vflipper = FlipperDeviceClass('vflipper', nameMagnet='vmag',
#    nameCounterTimerA='macr16',
#    nameCounterTimerB='macr18', nameCounterTimerC='macr19');












from time import sleep
from gda.device.scannable import PseudoDevice

import __main__ as gdamain

#The Class for creating a flipper based on the POMS magnet control 
class FlipperDeviceClass(PseudoDevice):
    """ This flips between two different field configurations in POMS, using the array
argument [field_Tesla, theta1_Deg, theta2_Deg, phi1_Deg, phi2_Deg, countTime_S,
          zeroRestTime_S]
    e.g.
    
    >>> pos vflipper [0.1 0 180 180 0 1.5 0.5]

It returns the 6 counter timer values (3 before and 3 after), plus several
calculations:

    EDIF =   (B2/A2) - (B1/A1)
    EXAS = ( (B2/A2) + (B1/A1) ) / 2.
    TDIF =   (C1/A1) - (C2/A2)
    TXAS = ( (C1/A1) + (C2/A2) ) / 2.

where A1, B1 & C1 are the counts at the demanded field, theta1 and phi1.
  and A2, B2 & C2 are the counts at the demanded field, theta2 and phi2.

The A channel is used to normalise the B and C channels.

To change the magnet scannable, call .setMagnet('magnet_name')
To change the counter timer scannables, call 
    .setCounters('nameCounterTimerA', 'nameCounterTimerB', 'nameCounterTimerC')
    e.g.
    >>> vflipper.setMagnet('vmag')
    >>> vflipper.setCounters('macr119', 'macr120', 'macr121')
    """
    def __init__(self, name, nameMagnet, nameCounterTimerA, nameCounterTimerB,
                 nameCounterTimerC):
        self.setName(name);
        self.setInputNames(['field', 'theta1', 'theta2', 'phi1', 'phi2',
                            'countTime', 'zeroRestTime']);
        #self.setExtraNames done in self.setCounters
        self.setOutputFormat(["%6.4f", "%6.3f", "%6.3f", "%6.3f", "%6.3f",
                              "%6.3f", "%6.3f"] + self.getExtraNameFormats());
        self.setLevel(7);
        self.magnet = vars(gdamain)[nameMagnet];
        self.setCounters(nameCounterTimerA, nameCounterTimerB, nameCounterTimerC)
        self.field=0;
        self.theta1=0;
        self.phi1=0;
        self.theta2=0;
        self.phi2=360;
        self.countTime=1;
        self.zeroRestTime=1;
        self.count1=[0, 0, 0];
        self.count2=[0, 0, 0];
        self.verbose=False

    def __repr__(self):
        format = "FlipperDeviceClass(name=%r, nameMagnet=%r," + \
            "nameCounterTimerA=%r, nameCounterTimerB=%r, nameCounterTimerC=%r)"
        return format % (self.name, self.magnet.name, self.counterA.name,
                         self.counterB.name, self.counterC.name)

    def setMagnet(self, nameMagnet):
        self.magnet = vars(gdamain)[nameMagnet];
        return;

    def setCounters(self, nameCounterTimerA, nameCounterTimerB, nameCounterTimerC):
        self.counterA = vars(gdamain)[nameCounterTimerA];
        self.counterB = vars(gdamain)[nameCounterTimerB];
        self.counterC = vars(gdamain)[nameCounterTimerC];
        self.setExtraNames(['A1'+nameCounterTimerA, 'A2'+nameCounterTimerA,
                            'B1'+nameCounterTimerB, 'B2'+nameCounterTimerB,
                            'C1'+nameCounterTimerC, 'C2'+nameCounterTimerC,
                            'EDIF', 'EXAS', 'TDIF', 'TXAS' ]);
        return;

    def getExtraNameFormats(self):
        return ["%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f",
                "%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f"]

    def getCounter(self):
        return self.counterA.name, self.counterB.name, self.counterC.name

    #PseudoDevice Implementation
    def atScanStart(self):
        return;

    def atScanEnd(self):
        return;
    
    def toString(self):
        ss=self.getName() + ": [field, theta1, theta2, phi1, phi2, countTime, zeroRestTime, countA1, countA2, countB1, countB2, countC1, countC2, EDIF, EXAS, TDIF, TXAS]: " + str(self.getPosition());
        return ss;

    def getPosition(self):
        A1, A2 = float(self.count1[0]), float(self.count2[0])
        B1, B2 = float(self.count1[1]), float(self.count2[1])
        C1, C2 = float(self.count1[2]), float(self.count2[2])
        try:
            EDIF =   (B2/A2) - (B1/A1)
        except ZeroDivisionError:
            EDIF = float('NaN')
        
        try:
            EXAS = ( (B2/A2) + (B1/A1) ) / 2.
        except ZeroDivisionError:
            EXAS = float('NaN')
        
        try:
            TDIF =   (C1/A1) - (C2/A2)
        except ZeroDivisionError:
            TDIF = float('NaN')
        
        try:
            TXAS = ( (C1/A1) + (C2/A2) ) / 2.
        except ZeroDivisionError:
            TXAS = float('NaN')
        
        return [self.field, self.theta1, self.theta2, self.phi1, self.phi2,
                self.countTime, self.zeroRestTime,
                self.count1[0], self.count2[0], self.count1[1], self.count2[1],
                self.count1[2], self.count2[2], EDIF, EXAS, TDIF, TXAS];
    
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
                self.counterC.getPosition()];

    def isBusy(self):
        sleep(1);
        return False;
