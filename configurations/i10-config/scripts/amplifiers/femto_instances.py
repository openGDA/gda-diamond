'''
Created on Aug 23, 2021

@author: fy65
'''
import installation
from utils.ExceptionLogs import localStation_exception
from amplifiers.dummyAutoGainAmplifer import DummyAutoGainAmplifier
from amplifiers.autoGainAmplifer import AutoGainAmplifier

import sys

if installation.isLive():
    try:
        #RASOR Femto
        rca1=AutoGainAmplifier("rca1", "ME01D-EA-IAMP-01", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        rca2=AutoGainAmplifier("rca2", "ME01D-EA-IAMP-02", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        rca3=AutoGainAmplifier("rca3", "ME01D-EA-IAMP-03", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        #Magnet Femto
        ca1je=AutoGainAmplifier("ca1je", "BL10J-EA-IAMP-01", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        ca2je=AutoGainAmplifier("ca2je", "BL10J-EA-IAMP-02", 0.5, 9.5, "%.4e")  # @UndefinedVariable
        ca3je=AutoGainAmplifier("ca3je", "BL10J-EA-IAMP-03", 0.5, 9.5, "%.4e")  # @UndefinedVariable
    except:
        localStation_exception(sys.exc_info(), "creating AutoGainAmplifer scannables")
else:
    #RASOR
    rca1=DummyAutoGainAmplifier("rca1", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    rca2=DummyAutoGainAmplifier("rca2", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    rca3=DummyAutoGainAmplifier("rca3", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    #Magnet
    ca1je=DummyAutoGainAmplifier("ca1je", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    ca2je=DummyAutoGainAmplifier("ca2je", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
    ca3je=DummyAutoGainAmplifier("ca3je", 10.0, 0.5, 9.5, "%.4e")  # @UndefinedVariable
