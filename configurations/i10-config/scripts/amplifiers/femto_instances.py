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
        # RASOR Femto
        rca1 = AutoGainAmplifier("rca1", "ME01D-EA-IAMP-01", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        rca2 = AutoGainAmplifier("rca2", "ME01D-EA-IAMP-02", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        rca3 = AutoGainAmplifier("rca3", "ME01D-EA-IAMP-03", 0.5, 9.5, "%.4e")  # @UndefinedVariable
    except:
        localStation_exception(sys.exc_info(), "creating AutoGainAmplifer scannables")
else:
    # RASOR
    rca1 = DummyAutoGainAmplifier("rca1", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    rca2 = DummyAutoGainAmplifier("rca2", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    rca3 = DummyAutoGainAmplifier("rca3", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
