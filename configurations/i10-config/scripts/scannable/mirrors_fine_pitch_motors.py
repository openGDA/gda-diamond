'''
Created on 10 Apr 2018

@author: fy65
'''
from utils.ExceptionLogs import localStation_exception
import sys
print "-"*100
print "Create scannables for mirror's fine pitch motors - using voltage control:"
print "    'm1fpitch', 'm3m5fpitch','m4fpitch','m6fpitch'"
try:
    from future.singleEpicsPositionerNoStatusClassDeadbandOrStop import SingleEpicsPositionerNoStatusClassDeadbandOrStop

    m1fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m1fpitch',
        'BL10I-OP-COL-01:FPITCH:DMD:AO', 'BL10I-OP-COL-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m3m5fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m3m5fpitch',
        'BL10I-OP-SWTCH-01:FPITCH:DMD:AO', 'BL10I-OP-SWTCH-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m4fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m4fpitch',
        'BL10I-OP-FOCS-01:FPITCH:DMD:AO', 'BL10I-OP-FOCS-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m6fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m6fpitch',
        'BL10J-OP-FOCA-01:FPITCH:DMD:AO', 'BL10J-OP-FOCA-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
except:
    localStation_exception(sys.exc_info(), "initialising fpitch scannables")
