'''
replace LEEM2000_scannable_ibit.py and leem_instances.py

added more scannables

@author: Fajin Yuan
@since: 2021-11-17
'''
from i06shared import installation
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class EpicsLEEMPVClass(ScannableMotionBase):
    '''Create PD to display single EPICS PV'''
    def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring="%.3f", readonly=False):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(5)
        self.incli=CAClient(pvinstring)
        self.outcli=CAClient(pvoutstring)
        self.read_only=readonly
        self.new_position = 0.0

    def rawGetPosition(self):
        output=0.0
        if installation.isDummy():
            return self.new_position
        try:
            if not self.outcli.isConfigured():
                self.outcli.configure()
            output=float(self.outcli.caget())
            output = self.getOutputFormat()[0] % output
            return float(output)
        except:
            print("%s: Error returning position" %(self.getName()))
            return 0

    def rawAsynchronousMoveTo(self,position):
        if self.read_only:
            print("%s: is a read-only scannable!" % (self.getName()))
            return
        self.new_position=position    # need this attribute for some other classes
        if installation.isDummy():
            return
        try:
            if self.incli.isConfigured():
                self.incli.caput(position)
            else:
                self.incli.configure()
                self.incli.caput(position)
        except:
            print("%s: error moving to position %f" % (self.getName(), float(position)))

    def isBusy(self):
        return 0

leem_stv = EpicsLEEMPVClass('leem_stv', "BL06I-EA-LEEM-01:START:VOLTAGE", "BL06I-EA-LEEM-01:START:VOLTAGE:RBV", "V", formatstring="%.3f")
leem_obj = EpicsLEEMPVClass('leem_obj', "BL06I-EA-LEEM-01:OBJECTIVE", "BL06I-EA-LEEM-01:OBJECTIVE:RBV", "mA", formatstring="%.3f")
leem_objStigmA = EpicsLEEMPVClass('leem_objStigmA', "BL06I-EA-LEEM-01:OBJSTIGMA", "BL06I-EA-LEEM-01:OBJSTIGMA:RBV", "mA", formatstring="%.3f")
leem_objStigmB = EpicsLEEMPVClass('leem_objStigmB', "BL06I-EA-LEEM-01:OBJSTIGMB", "BL06I-EA-LEEM-01:OBJSTIGMB:RBV", "mA", formatstring="%.3f")
leem_p3alignx = EpicsLEEMPVClass('leem_p3alignx', "BL06I-EA-LEEM-01:P3ALIGNX", "BL06I-EA-LEEM-01:P3ALIGNX:RBV", "mA", formatstring="%.3f")
leem_p3aligny = EpicsLEEMPVClass('leem_p3aligny',"BL06I-EA-LEEM-01:P3ALIGNY", "BL06I-EA-LEEM-01:P3ALIGNY:RBV", "mA", formatstring="%.3f")
leem_transferlens = EpicsLEEMPVClass('leem_transferlens', "BL06I-EA-LEEM-01:TRANSFER:LENS", "BL06I-EA-LEEM-01:TRANSFER:LENS:RBV", "mA", formatstring="%.3f")
leem_temp = EpicsLEEMPVClass('leem_temp',"BL06I-EA-LEEM-01:SAMPLE:TEMP", "BL06I-EA-LEEM-01:SAMPLE:TEMP:RBV", "C", formatstring="%.2f")
leem_objAlignX = EpicsLEEMPVClass('leem_objAlignX', "BL06I-EA-LEEM-01:OBJALIGNX", "BL06I-EA-LEEM-01:OBJALIGNX:RBV", "mA", formatstring="%.3f")
leem_objAlignY = EpicsLEEMPVClass('leem_objAlignY', "BL06I-EA-LEEM-01:OBJALIGNY", "BL06I-EA-LEEM-01:OBJALIGNY:RBV", "mA", formatstring="%.3f")
leem_rot = EpicsLEEMPVClass('leem_rot',"", "BL06I-EA-LEEM-01:IMAGE:ROT:RBV", "deg", formatstring="%.4f", readonly=True)
leem_intermlens = EpicsLEEMPVClass('leem_intermlens', "BL06I-EA-LEEM-01:INTERM:LENS", "BL06I-EA-LEEM-01:INTERM:LENS:RBV", "mA", formatstring="%.3f")
leem_FOV_A = EpicsLEEMPVClass('leem_FOV_A',"", "BL06I-EA-LEEM-01:FOV:RBV", "um", formatstring="%.2f", readonly=True)
leem_FOV_B = EpicsLEEMPVClass('leem_FOV_B',"", "BL06I-EA-LEEM-01:FOVB:RBV", "um", formatstring="%.2f", readonly=True)

    