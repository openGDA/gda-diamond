'''
Created on 10 Apr 2018

@author: fy65
'''

print "-"*100
print "ID motions scannables to work around EPICS caput callback issues in I10"
## temporary fix for inability to perform caput with callback on SR10I-MO-SERVC-01:BLGAPMTR.VAL
from gdascripts.pd.epics_pds import SingleEpicsPositionerClass
idd_gap_temp = SingleEpicsPositionerClass("idd_gap_temp",
                    "SR10I-MO-SERVC-01:BLGAPMTR.VAL", 
                    "SR10I-MO-SERVC-01:BLGAPMTR.RBV", 
                    "SR10I-MO-SERVC-01:BLGAPMTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLGAPMTR.STOP", "mm", "%.4f")

idu_gap_temp = SingleEpicsPositionerClass("idu_gap_temp",
                    "SR10I-MO-SERVC-21:BLGAPMTR.VAL", 
                    "SR10I-MO-SERVC-21:BLGAPMTR.RBV", 
                    "SR10I-MO-SERVC-21:BLGAPMTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLGAPMTR.STOP", "mm", "%.4f")

idd_rowphase1_temp = SingleEpicsPositionerClass("idd_rowphase1_temp",
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ1MTR.STOP", "mm", "%.4f")

idu_rowphase1_temp = SingleEpicsPositionerClass("idu_rowphase1_temp",
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ1MTR.STOP", "mm", "%.4f")

idd_rowphase2_temp = SingleEpicsPositionerClass("idd_rowphase2_temp",
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ2MTR.STOP", "mm", "%.4f")

idu_rowphase2_temp = SingleEpicsPositionerClass("idu_rowphase2_temp",
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ2MTR.STOP", "mm", "%.4f")

idd_rowphase3_temp = SingleEpicsPositionerClass("idd_rowphase3_temp",
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ3MTR.STOP", "mm", "%.4f")

idu_rowphase3_temp = SingleEpicsPositionerClass("idu_rowphase3_temp",
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ3MTR.STOP", "mm", "%.4f")

idd_rowphase4_temp = SingleEpicsPositionerClass("idd_rowphase4_temp",
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.VAL", 
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.RBV", 
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLRPQ4MTR.STOP", "mm", "%.4f")

idu_rowphase4_temp = SingleEpicsPositionerClass("idu_rowphase4_temp",
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.VAL", 
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.RBV", 
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLRPQ4MTR.STOP", "mm", "%.4f")

idd_jawphase_temp = SingleEpicsPositionerClass("idd_jawphase_temp",
                    "SR10I-MO-SERVC-01:BLJAWMTR.VAL", 
                    "SR10I-MO-SERVC-01:BLJAWMTR.RBV", 
                    "SR10I-MO-SERVC-01:BLJAWMTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLJAWMTR.STOP", "mm", "%.4f")

idu_jawphase_temp = SingleEpicsPositionerClass("idu_jawphase_temp",
                    "SR10I-MO-SERVC-21:BLJAWMTR.VAL", 
                    "SR10I-MO-SERVC-21:BLJAWMTR.RBV", 
                    "SR10I-MO-SERVC-21:BLJAWMTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLJAWMTR.STOP", "mm", "%.4f")

idd_sepphase_temp = SingleEpicsPositionerClass("idd_sepphase_temp",
                    "SR10I-MO-SERVC-01:BLSEPMTR.VAL", 
                    "SR10I-MO-SERVC-01:BLSEPMTR.RBV", 
                    "SR10I-MO-SERVC-01:BLSEPMTR.DMOV", 
                    "SR10I-MO-SERVC-01:BLSEPMTR.STOP", "mm", "%.4f")

idu_sepphase_temp = SingleEpicsPositionerClass("idu_sepphase_temp",
                    "SR10I-MO-SERVC-21:BLSEPMTR.VAL", 
                    "SR10I-MO-SERVC-21:BLSEPMTR.RBV", 
                    "SR10I-MO-SERVC-21:BLSEPMTR.DMOV", 
                    "SR10I-MO-SERVC-21:BLSEPMTR.STOP", "mm", "%.4f")

print " To move gap use idd_gap_temp as idd_gap etc."