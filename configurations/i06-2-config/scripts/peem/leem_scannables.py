'''
replace LEEM2000_scannable_init.py and leem_instances.py

added more scannables

@author: Fajin Yuan
@since: 2021-11-17
'''
from i06shared import installation
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep

class EpicsLEEMPVClass(ScannableMotionBase):
    '''Create scannable to control and display each LEEM field parameters implemented in EPICS'''
    def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring="%.3f", readonly=False):
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.formatstring = formatstring
        self.setLevel(5)
        self.incli=CAClient(pvinstring)
        self.outcli=CAClient(pvoutstring)
        self.read_only=readonly
        self.new_position = 0.0

    def rawGetPosition(self):
        output = 0.0
        if installation.isDummy():
            return self.new_position
        try:
            if not self.outcli.isConfigured():
                self.outcli.configure()
            self.setOutputFormat([self.formatstring])
            output = float(self.outcli.caget())
            return output
        except Exception as e:
            self.setOutputFormat(["%s"])
            return "%s: %s - %s" % (self.getName(), self.outcli.getPvName(), e.getMessage())

    def rawAsynchronousMoveTo(self,position):
        if self.read_only:
            print("%s: is a read-only scannable!" % (self.getName()))
            return
        self.new_position = position
        if installation.isDummy():
            return
        try:
            if self.incli.isConfigured():
                self.incli.caput(position)
            else:
                self.incli.configure()
                self.incli.caput(position)
        except Exception as e:
            print("%s: error moving %s to position %f. %s" % (self.getName(), self.incli.getPvName(), float(position), e.getMessage()))

    def isBusy(self):
        return False

class EpicsLEEMCoupledScannable(ScannableMotionBase):
    '''Create scannable to control and display each LEEM field parameters implemented in EPICS'''
    def __init__(self, name, value_scannable, index_scannable, ps_index_value):
        self.setName(name);
        self.setInputNames([name])
        self.value_scannable = value_scannable
        self.index_scannable = index_scannable
        self.setOutputFormat([value_scannable.getOutputFormat()[0]])
        self.ps_index_value = ps_index_value
        self.setLevel(5)
        self.inScan = False
        self.__busy = False
        
    def configure(self):
        self.index_scannable.moveTo(self.ps_index_value)
        sleep(0.5)

    def atScanStart(self):
        self.inScan = True
        self.configure()    

    def rawGetPosition(self):
        if not self.inScan:
            self.configure()
        return self.value_scannable.getPosition()

    def rawAsynchronousMoveTo(self,position):
        self.__busy = True
        if not self.inScan:
            self.configure()
        self.value_scannable.rawAsynchronousMoveTo(float(position))
        sleep(0.1)
        self.__busy = False

    def isBusy(self):
        return self.__busy

    def atScanEnd(self):
        self.inScan = False
        self.__busy = False

    def stop(self):
        self.inScan = False
        self.__busy = False

    def atCommandFailure(self):
        self.inScan = False
        self.__busy = False

leem_stv = EpicsLEEMPVClass('leem_stv', "BL06K-EA-LEEM-01:START:VOLTAGE", "BL06K-EA-LEEM-01:START:VOLTAGE:RBV", "V", formatstring="%.3f")
leem_obj = EpicsLEEMPVClass('leem_obj', "BL06K-EA-LEEM-01:OBJECTIVE", "BL06K-EA-LEEM-01:OBJECTIVE:RBV", "mA", formatstring="%.3f")
leem_objStigmA = EpicsLEEMPVClass('leem_objStigmA', "BL06K-EA-LEEM-01:OBJSTIGMA", "BL06K-EA-LEEM-01:OBJSTIGMA:RBV", "mA", formatstring="%.3f")
leem_objStigmB = EpicsLEEMPVClass('leem_objStigmB', "BL06K-EA-LEEM-01:OBJSTIGMB", "BL06K-EA-LEEM-01:OBJSTIGMB:RBV", "mA", formatstring="%.3f")
leem_p3alignx = EpicsLEEMPVClass('leem_p3alignx', "BL06K-EA-LEEM-01:P3ALIGNX", "BL06K-EA-LEEM-01:P3ALIGNX:RBV", "mA", formatstring="%.3f")
leem_p3aligny = EpicsLEEMPVClass('leem_p3aligny',"BL06K-EA-LEEM-01:P3ALIGNY", "BL06K-EA-LEEM-01:P3ALIGNY:RBV", "mA", formatstring="%.3f")
leem_transferlens = EpicsLEEMPVClass('leem_transferlens', "BL06K-EA-LEEM-01:TRANSFER:LENS", "BL06K-EA-LEEM-01:TRANSFER:LENS:RBV", "mA", formatstring="%.3f")
leem_temp = EpicsLEEMPVClass('leem_temp',"BL06K-EA-LEEM-01:SAMPLE:TEMP", "BL06K-EA-LEEM-01:SAMPLE:TEMP:RBV", "C", formatstring="%.2f")
leem_objAlignX = EpicsLEEMPVClass('leem_objAlignX', "BL06K-EA-LEEM-01:OBJALIGNX", "BL06K-EA-LEEM-01:OBJALIGNX:RBV", "mA", formatstring="%.3f")
leem_objAlignY = EpicsLEEMPVClass('leem_objAlignY', "BL06K-EA-LEEM-01:OBJALIGNY", "BL06K-EA-LEEM-01:OBJALIGNY:RBV", "mA", formatstring="%.3f")
leem_rot = EpicsLEEMPVClass('leem_rot',"", "BL06K-EA-LEEM-01:CALC:ROT:ANGLE", "deg", formatstring="%.4f", readonly=True)
leem_intermlens = EpicsLEEMPVClass('leem_intermlens', "BL06K-EA-LEEM-01:INTERM:LENS", "BL06K-EA-LEEM-01:INTERM:LENS:RBV", "mA", formatstring="%.3f")
leem_FOV_A = EpicsLEEMPVClass('leem_FOV_A',"", "BL06K-EA-LEEM-01:FOV:RBV", "um", formatstring="%.2f", readonly=True)
leem_FOV_B = EpicsLEEMPVClass('leem_FOV_B',"", "BL06K-EA-LEEM-01:FOVB:RBV", "um", formatstring="%.2f", readonly=True)
leem_PS_index = EpicsLEEMPVClass('leem_PS_index',"BL06K-EA-LEEM-01:PS:INDEX", "BL06K-EA-LEEM-01:PS:INDEX", "", formatstring="%d")
leem_PS_value = EpicsLEEMPVClass('leem_PS_value',"BL06K-EA-LEEM-01:PS", "BL06K-EA-LEEM-01:PS:RBV", "", formatstring="%.3f")
leem_ill_eq_x = EpicsLEEMCoupledScannable('leem_ill_eq_x', leem_PS_value, leem_PS_index, 30)
leem_ill_eq_y = EpicsLEEMCoupledScannable('leem_ill_eq_y', leem_PS_value, leem_PS_index, 31)

