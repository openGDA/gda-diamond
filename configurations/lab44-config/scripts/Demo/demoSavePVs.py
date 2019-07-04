
from gda.epics.util import EpicsPVs

pvs = EpicsPVs();
pvs.addPV("s1Y","BL06I-AL-SLITS-01:Y:POS.VAL")
pvs.addPV("d2X","BL06I-DI-PHDGN-02:X.VAL")

#Save the PVs added before a scan
pvs.preScanSave();

scan testMotor1 0 10 1

#Save the PVs after a scan
pvs.afterScanSave();

#clear all PVs if necessary
pvs.clearPVs();