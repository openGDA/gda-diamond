'''
Created on 10 Apr 2018

@author: fy65
'''
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
import gda
from utils.ExceptionLogs import localStation_exception
import sys
print "-"*100
print "Creating scannables for Front End Beam Monitor - 'xbpm'"
try:
    xbpm1_x = DisplayEpicsPVClass('xbpm1_x', 'FE10I-DI-PBPM-01:BEAMX', 'nm', '%f')
    xbpm1_y = DisplayEpicsPVClass('xbpm1_y', 'FE10I-DI-PBPM-01:BEAMY', 'nm', '%f')
    xbpm2_x = DisplayEpicsPVClass('xbpm2_x', 'FE10I-DI-PBPM-02:BEAMX', 'nm', '%f')
    xbpm2_y = DisplayEpicsPVClass('xbpm2_y', 'FE10I-DI-PBPM-02:BEAMY', 'nm', '%f')
    xbpm_anglex = DisplayEpicsPVClass('xbpm_anglex', 'FE10I-DI-BEAM-01:RM:ANGLEX', 'rad', '%f')
    xbpm_angley = DisplayEpicsPVClass('xbpm_angley', 'FE10I-DI-BEAM-01:RM:ANGLEY', 'rad', '%f')
    xbpm_anglex_urad = DisplayEpicsPVClass('xbpm_anglex_urad', 'FE10I-DI-BEAM-01:X:ANGLE', 'urad', '%f')
    xbpm_angley_urad = DisplayEpicsPVClass('xbpm_angley_urad', 'FE10I-DI-BEAM-01:Y:ANGLE', 'urad', '%f')
    xbpm=gda.device.scannable.scannablegroup.ScannableGroup('xbpm', [
        xbpm1_x, xbpm1_y, xbpm2_x, xbpm2_y,
        xbpm_anglex, xbpm_angley, xbpm_anglex_urad, xbpm_angley_urad])
except:
    localStation_exception(sys.exc_info(), "initialising front end xbpm's")