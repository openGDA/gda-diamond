'''
Created on 10 Apr 2018

@author: fy65
'''

from gda.device.scannable.scannablegroup import ScannableGroup
from utils.ExceptionLogs import localStation_exception
import installation
print "-"*100
print "Creating scannables for Front End Beam Monitor - 'xbpm'"
if installation.isLive():
    try:
        from gdascripts.pd.epics_pds import DisplayEpicsPVClass
        xbpm1_x = DisplayEpicsPVClass('xbpm1_x', 'FE10I-DI-PBPM-01:BEAMX', 'mm', '%f')
        xbpm1_y = DisplayEpicsPVClass('xbpm1_y', 'FE10I-DI-PBPM-01:BEAMY', 'mm', '%f')
        xbpm2_x = DisplayEpicsPVClass('xbpm2_x', 'FE10I-DI-PBPM-02:BEAMX', 'mm', '%f')
        xbpm2_y = DisplayEpicsPVClass('xbpm2_y', 'FE10I-DI-PBPM-02:BEAMY', 'mm', '%f')
        xbpm_anglex = DisplayEpicsPVClass('xbpm_anglex', 'FE10I-DI-BEAM-01:RM:ANGLEX', 'mrad', '%f')
        xbpm_angley = DisplayEpicsPVClass('xbpm_angley', 'FE10I-DI-BEAM-01:RM:ANGLEY', 'mrad', '%f')
        xbpm_anglex_urad = DisplayEpicsPVClass('xbpm_anglex_urad', 'FE10I-DI-BEAM-01:X:ANGLE', 'urad', '%f')
        xbpm_angley_urad = DisplayEpicsPVClass('xbpm_angley_urad', 'FE10I-DI-BEAM-01:Y:ANGLE', 'urad', '%f')
        xbpm = ScannableGroup('xbpm', [xbpm1_x, xbpm1_y, xbpm2_x, xbpm2_y, xbpm_anglex, xbpm_angley, xbpm_anglex_urad, xbpm_angley_urad])
    except:
        localStation_exception(sys.exc_info(), "initialising front end xbpm's")
else:
    from gdascripts.pd.dummy_pds import DummyDisplayEpicsPVClass
    xbpm1_x = DummyDisplayEpicsPVClass('xbpm1_x', -5.0, 5.0, 'mm', '%f')
    xbpm1_y = DummyDisplayEpicsPVClass('xbpm1_y', -5.0, 5.0, 'mm', '%f')
    xbpm2_x = DummyDisplayEpicsPVClass('xbpm2_x', -5.0, 5.0, 'mm', '%f')
    xbpm2_y = DummyDisplayEpicsPVClass('xbpm2_y', -5.0, 5.0, 'mm', '%f')
    xbpm_anglex = DummyDisplayEpicsPVClass('xbpm_anglex', 0.0, 10.0, 'mrad', '%f')
    xbpm_angley = DummyDisplayEpicsPVClass('xbpm_angley', 0.0, 10.0, 'mrad', '%f')
    xbpm_anglex_urad = DummyDisplayEpicsPVClass('xbpm_anglex_urad', 0.0, 10.0, 'urad', '%f')
    xbpm_angley_urad = DummyDisplayEpicsPVClass('xbpm_angley_urad', 0.0, 10.0, 'urad', '%f')
    xbpm = ScannableGroup('xbpm', [xbpm1_x, xbpm1_y, xbpm2_x, xbpm2_y, xbpm_anglex, xbpm_angley, xbpm_anglex_urad, xbpm_angley_urad])
    