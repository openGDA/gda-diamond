from gdascripts.messages import handle_messages
from gda.jython.commands import GeneralCommands
from gdascripts.utils import caput, caget
from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.GeneralCommands import alias, vararg_alias

from gdascripts.pd.epics_pds import DisplayEpicsPVClass, EpicsReadWritePVClass

dcm1_cap_1 = DisplayEpicsPVClass('dcm1_cap_1', 'BL12I-OP-DCM-01:BEND:XTAL1:CAP1', 'microns', '%.3f')
dcm1_cap_2 = DisplayEpicsPVClass('dcm1_cap_2', 'BL12I-OP-DCM-01:BEND:XTAL1:CAP2', 'microns', '%.3f')
dcm2_cap_1 = DisplayEpicsPVClass('dcm2_cap_1', 'BL12I-OP-DCM-01:BEND:XTAL2:CAP1', 'microns', '%.3f')
dcm2_cap_2 = DisplayEpicsPVClass('dcm2_cap_2', 'BL12I-OP-DCM-01:BEND:XTAL2:CAP2', 'microns', '%.3f')
dcm1_bender_sync = EpicsReadWritePVClass('dcm1_bender_sync', 'BL12I-OP-DCM-01:XTAL1:BEND:SYNC:DEMAND', 'microns', '%.3g')
dcm2_bender_sync = EpicsReadWritePVClass('dcm2_bender_sync', 'BL12I-OP-DCM-01:XTAL2:BEND:SYNC:DEMAND', 'microns', '%.3g')

dcm1_bender_1_offset = EpicsReadWritePVClass('dcm1_bender_1_offset', 'BL12I-OP-DCM-01:XTAL1:IN.OFF', 'microns', '%.3g')
dcm1_bender_2_offset = EpicsReadWritePVClass('dcm1_bender_2_offset', 'BL12I-OP-DCM-01:XTAL1:OUT.OFF', 'microns', '%.3g')

dcm2_bender_1_offset = EpicsReadWritePVClass('dcm2_bender_1_offset', 'BL12I-OP-DCM-01:XTAL2:IN.OFF', 'microns', '%.3g')
dcm2_bender_2_offset = EpicsReadWritePVClass('dcm2_bender_2_offset', 'BL12I-OP-DCM-01:XTAL2:OUT.OFF', 'microns', '%.3g')

#dcm1_clear_bender_offsets = EpicsReadWritePVClass('dcm1_clear_bender_offsets', 'BL12I-OP-DCM-01:XTAL1:CLEAROFF.PROC', '', '%.3g')
#dcm2_clear_bender_offsets = EpicsReadWritePVClass('dcm2_clear_bender_offsets', 'BL12I-OP-DCM-01:XTAL2:CLEAROFF.PROC', '', '%.3g')

def dcm1_clear_bender_offsets():
    caput ("BL12I-OP-DCM-01:XTAL1:CLEAROFF.PROC", 1)
alias("dcm1_clear_bender_offsets")

def dcm2_clear_bender_offsets():
    caput ("BL12I-OP-DCM-01:XTAL2:CLEAROFF.PROC", 1)
alias("dcm2_clear_bender_offsets")

def dcm1_bender_driveaway():
    caput ("BL12I-OP-DCM-01:XTAL1:DRIVEOFF.PROC", 1)
alias("dcm1_bender_driveaway")

def dcm2_bender_driveaway():
    caput ("BL12I-OP-DCM-01:XTAL2:DRIVEOFF.PROC", 1)
alias("dcm2_bender_driveaway")

def dcm1_cap_zero():
    caput ("BL12I-OP-DCM-01:BEND:XTAL1:CAP:CLEAROFF.PROC", 1)
alias("dcm1_cap_zero")

def dcm2_cap_zero():
    caput ("BL12I-OP-DCM-01:BEND:XTAL2:CAP:CLEAROFF.PROC", 1)
alias("dcm2_cap_zero")

def dcm1_set_bender_offsets():
    caput ("BL12I-OP-DCM-01:XTAL1:SETBENDOFF.PROC", 1)
alias("dcm1_set_bender_offsets")

def dcm2_set_bender_offsets():
    caput ("BL12I-OP-DCM-01:XTAL2:SETBENDOFF.PROC", 1)
alias("dcm2_set_bender_offsets")




