'''
Created on Aug 23, 2021

@author: fy65
'''
from i10shared import installation
from utils.ExceptionLogs import localStation_exception
from amplifier.dummyAutoGainAmplifer import DummyAutoGainAmplifier
from amplifier.autoGainAmplifer import AutoGainAmplifier

import sys

if installation.isLive():
    try:
        # HFM Femto
        ca1je = AutoGainAmplifier("ca1je", "BL10J-EA-IAMP-01", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        ca2je = AutoGainAmplifier("ca2je", "BL10J-EA-IAMP-02", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        ca3je = AutoGainAmplifier("ca3je", "BL10J-EA-IAMP-03", 0.5, 9.5, "%.4e")  # @UndefinedVariable
    except:
        localStation_exception(sys.exc_info(), "creating AutoGainAmplifer scannables")
else:
    # Magnet
    ca1je = DummyAutoGainAmplifier("ca1je", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    ca2je = DummyAutoGainAmplifier("ca2je", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    ca3je = DummyAutoGainAmplifier("ca3je", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
