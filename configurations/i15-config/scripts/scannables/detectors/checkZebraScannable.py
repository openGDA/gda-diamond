from gda.device.scannable import ScannableBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.scannable.epics.PvManager import PvManager
from time import sleep

TIMEOUT=5

class ZebraPositionScannable(ScannableBase):
    """ Since this scannable causes the zebra position compare configuration to be overwritten, the only scan we can use it in is
        one which doesn't make any other use of the Zebra position compare functionality.
    """
    def __init__(self, name, zebraRootPV, check_scannable, zebra_scannable):
        self.check_scannable = check_scannable
        self.zebra_scannable = zebra_scannable
        self.pvs = PvManager(pvroot = zebraRootPV)
        self._setNames(name)
        self.setLevel(5)
        self.verbose=True

    def _setNames(self, name):
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames([self.check_scannable.name, 'diff']);
        self.setOutputFormat(["%5.5g", "%5.5g", "%5.5g"])

    def rawGetPosition(self):
        return self.zebraGetPosition()
    
    def zebraGetPosition(self):
        last_encoder_pv = 'PC_ENC{}_LAST'.format(self.zebra_scannable.getPcEnc()+1)
        position = float(self.pvs[last_encoder_pv].caget())
        check_position = self.check_scannable.getPosition()
        return [position, check_position, position - check_position]

    def rawAsynchronousMoveTo(self, new_position):
        return self.zebraRawAsynchronousMoveTo(new_position)

    def zebraRawAsynchronousMoveTo(self, new_position):
        simpleLog("Performing a Zebra time scan to check position of {}, new_position value ({}) is ignored & motor not moved...".format(
            self.check_scannable.getName(), new_position))
        # Reset the zebra box before trying to set any parameters
        self.pvs['SYS_RESET.PROC'].caput(TIMEOUT, 1)
        
        while self.isBusy():
            if self.verbose: simpleLog("Waiting for zebra to disarm before...")
            sleep(0.5)

        pc_bit_cap = 960 | (1 << self.zebra_scannable.getPcEnc())
        self.pvs['PC_TSPRE'      ].caput(TIMEOUT, 'ms')
        self.pvs['PC_BIT_CAP'    ].caput(TIMEOUT, pc_bit_cap)      # Complex bitfield
        
        self.pvs['PC_ARM_SEL'    ].caput(TIMEOUT, 'Soft')
        self.pvs['PC_GATE_SEL'   ].caput(TIMEOUT, 'Time')
        self.pvs['PC_GATE_START' ].caput(TIMEOUT, 0)
        self.pvs['PC_GATE_WID'   ].caput(TIMEOUT, 1)
        self.pvs['PC_GATE_NGATE' ].caput(TIMEOUT, 1)
        
        self.pvs['PC_PULSE_SEL'  ].caput(TIMEOUT, 'Time')
        self.pvs['PC_PULSE_START'].caput(TIMEOUT, 0)
        self.pvs['PC_PULSE_WID'  ].caput(TIMEOUT, 1)
        self.pvs['PC_PULSE_STEP' ].caput(TIMEOUT, 1+0.0002) # PULSE_STEP *must* be bigger than PULSE_WID, maybe more than 0.0001 bigger
        self.pvs['PC_PULSE_DLY'  ].caput(TIMEOUT, 1)
        self.pvs['PC_PULSE_MAX'  ].caput(TIMEOUT, 1)
        
        self.pvs['PC_ARM'].caput(TIMEOUT, 1)
        return

    def copyMotorPosToZebra(self):
        self.pvs['M1:SETPOS.PROC'].caput(TIMEOUT, 1)

    def isBusy(self):
        return self.zebraIsBusy()

    def zebraIsBusy(self):
        pc_arm_out = self.pvs['PC_ARM_OUT'].caget()
        return (pc_arm_out == '1.0')

    def stop(self):
        self.pvs['SYS_RESET.PROC'].caput(TIMEOUT, 1)
        return

""" Since this scannable causes the zebra position compare configuration to be overwritten and the only time we would want to use
    it would be to protect a Zebra position compare scan from failing, we can't actually use this right now. We would need to find
    another way to extract the current zebra motor position from the Zebra box.

class ZebraCheckScannable(ZebraPositionScannable):
    def __init__(self, name, zebraRootPV, check_scannable):
        ZebraPositionScannable.__init__(self, name, zebraRootPV, check_scannable)
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([]);
        self.setOutputFormat([])
        
    def atScanStart(self):
        diff = 1
        
        while abs(diff) > 0.0001:
            self.zebraRawAsynchronousMoveTo(1)
            while self.zebraIsBusy():
                if self.verbose: simpleLog("Waiting for zebra to disarm after...")
                sleep(0.5)
            position, check_position, diff = self.zebraGetPosition()
            if self.verbose: simpleLog("zebra is at %f, while %s is static at position %f, with diff=%f..." % (position, self.check_scannable.name, check_position, diff))
            if abs(diff) < 0.0001:
                break
            simpleLog("Run the command '%s.copyMotorPosToZebra()' fix this..." % self.name)
            sleep(5)

    def atScanEnd(self):
        pass

    def rawGetPosition(self):
        return None

    def rawAsynchronousMoveTo(self, new_position):
        return None

    def isBusy(self):
        return False
"""