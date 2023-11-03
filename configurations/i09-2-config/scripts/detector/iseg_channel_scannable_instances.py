'''
Created on 24 Aug 2023

@author: fy65
'''
from detector.iseg_control_scannable_class import ISegChannelControlScannable
from gda.jython.commands.GeneralCommands import alias
from detector.iseg_group_class import ISegGroup

ISEG_DEVICE_PV = "BL09K-EA-PSU-01:0"

m0c0 = ISegChannelControlScannable("m0c0", 0, 0, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c0.configure()
m0c1 = ISegChannelControlScannable("m0c1", 0, 1, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c1.configure()
m0c2 = ISegChannelControlScannable("m0c2", 0, 2, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c2.configure()
m0c3 = ISegChannelControlScannable("m0c3", 0, 3, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c3.configure()
m0c4 = ISegChannelControlScannable("m0c4", 0, 4, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c4.configure()
m0c5 = ISegChannelControlScannable("m0c5", 0, 5, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c5.configure()
m0c6 = ISegChannelControlScannable("m0c6", 0, 6, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c6.configure()
m0c7 = ISegChannelControlScannable("m0c7", 0, 7, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m0c7.configure()

m1c0 = ISegChannelControlScannable("m1c0", 1, 0, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c0.configure()
m1c1 = ISegChannelControlScannable("m1c1", 1, 1, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c1.configure()
m1c2 = ISegChannelControlScannable("m1c2", 1, 2, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c2.configure()
m1c3 = ISegChannelControlScannable("m1c3", 1, 3, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c3.configure()
m1c4 = ISegChannelControlScannable("m1c4", 1, 4, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c4.configure()
m1c5 = ISegChannelControlScannable("m1c5", 1, 5, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c5.configure()
m1c6 = ISegChannelControlScannable("m1c6", 1, 6, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c6.configure()
m1c7 = ISegChannelControlScannable("m1c7", 1, 7, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m1c7.configure()

m2c0 = ISegChannelControlScannable("m2c0", 2, 0, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c0.configure()
m2c1 = ISegChannelControlScannable("m2c1", 2, 1, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c1.configure()
m2c2 = ISegChannelControlScannable("m2c2", 2, 2, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c2.configure()
m2c3 = ISegChannelControlScannable("m2c3", 2, 3, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c3.configure()
m2c4 = ISegChannelControlScannable("m2c4", 2, 4, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c4.configure()
m2c5 = ISegChannelControlScannable("m2c5", 2, 5, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c5.configure()
m2c6 = ISegChannelControlScannable("m2c6", 2, 6, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c6.configure()
m2c7 = ISegChannelControlScannable("m2c7", 2, 7, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m2c7.configure()

m3c0 = ISegChannelControlScannable("m3c0", 3, 0, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c0.configure()
m3c1 = ISegChannelControlScannable("m3c1", 3, 1, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c1.configure()
m3c2 = ISegChannelControlScannable("m3c2", 3, 2, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c2.configure()
m3c3 = ISegChannelControlScannable("m3c3", 3, 3, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c3.configure()
m3c4 = ISegChannelControlScannable("m3c4", 3, 4, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c4.configure()
m3c5 = ISegChannelControlScannable("m3c5", 3, 5, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c5.configure()
m3c6 = ISegChannelControlScannable("m3c6", 3, 6, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c6.configure()
m3c7 = ISegChannelControlScannable("m3c7", 3, 7, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m3c7.configure()

m4c0 = ISegChannelControlScannable("m4c0", 4, 0, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c0.configure()
m4c1 = ISegChannelControlScannable("m4c1", 4, 1, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c1.configure()
m4c2 = ISegChannelControlScannable("m4c2", 4, 2, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c2.configure()
m4c3 = ISegChannelControlScannable("m4c3", 4, 3, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c3.configure()
m4c4 = ISegChannelControlScannable("m4c4", 4, 4, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c4.configure()
m4c5 = ISegChannelControlScannable("m4c5", 4, 5, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c5.configure()
m4c6 = ISegChannelControlScannable("m4c6", 4, 6, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c6.configure()
m4c7 = ISegChannelControlScannable("m4c7", 4, 7, pv_root = ISEG_DEVICE_PV, tolerance = 0.1, voltage_ramp_speed = 1.0, current_ramp_speed = 1.0, voltage_control = True); m4c7.configure()

hda_group = [m1c0, m0c2, m0c3, m0c4, m0c5, m0c6, m0c7]
main_lenses_group = [m3c0, m3c1, m3c2, m3c3, m3c4, m3c5, m3c6, m0c0, m0c1]
stig_group = [m2c0, m2c1, m2c2, m2c3, m2c4, m2c5, m2c6, m2c7, m4c0, m4c1, m4c2, m4c3, m4c4, m4c5, m4c6, m4c7]
downstream_group = [m1c1, m1c2, m1c3, m1c4, m1c7]
HDA_PEEM_group = [m1c0, m0c2, m0c3, m0c5, m0c6, m1c7]
MM_group = [m1c0, m0c2, m0c3, m0c4, m0c5, m0c6, m0c7,m3c0, m3c1, m3c2, m3c3, m3c4, m3c5, m3c6, m0c0, m0c1,m2c0, m2c1, m2c2, m2c3, m2c4, m2c5, m2c6, m2c7, m4c0, m4c1, m4c2, m4c3, m4c4, m4c5, m4c6, m4c7,m1c1, m1c2, m1c3, m1c4, m1c6, m1c7]

hda = ISegGroup("hda", hda_group)
mainlenses = ISegGroup("mainlenses", main_lenses_group)
stig = ISegGroup("stig", stig_group)
downstream = ISegGroup("downstream", downstream_group)
hda_peem = ISegGroup("hda_peem", HDA_PEEM_group)
MM = ISegGroup("MM", MM_group)


def hda_on(group=hda_group):
    [each.on() for each in group]
def hda_off(group=hda_group):
    [each.off() for each in group]
alias("hda_on")
alias("hda_off")

def mainlenses_on(group = main_lenses_group):
    [each.on() for each in group]
def mainlenses_off(group = main_lenses_group):
    [each.off() for each in group]
alias("mainlenses_on")
alias("mainlenses_off")
    
def stig_on(group = stig_group):
    [each.on() for each in group]
def stig_off(group = stig_group):
    [each.off() for each in group]
alias("stig_on")
alias("stig_off")
    
def downstream_on(group = downstream_group):
    [each.on() for each in group]
def downstream_off(group = downstream_group):
    [each.off() for each in group]
alias("downstream_on")
alias("downstream_off")

def hda_peem_on(group=HDA_PEEM_group):
    [each.on() for each in group]
def hda_peem_off(group=HDA_PEEM_group):
    [each.off() for each in group]
def hda_peem_set(voltage, group=HDA_PEEM_group):
    [each.rawAsynchronousMoveTo(voltage) for each in group]
alias("hda_peem_on")
alias("hda_peem_off")

def MM_on(group=MM_group):
    [each.on() for each in group]
def MM_off(group=MM_group):
    [each.off() for each in group]
alias("MM_on")
alias("MM_off")


print("iSeg scannable initialisation completed!")
