from gdascripts import installation as installation
from i09shared.scannable.energyHarmonicOrder import EnergyHarmonicOrder
from i09shared.pseudodevices.idgap_offset import IDGapOffset
from i09_1_shared.calibration.hardenergy import HardEnergy
from gdaserver import igap, dcmenergy #@UnresolvedImport
igap_offset = IDGapOffset("igap_offset")
print("-"*100)
print("Create an 'ienergy_s' scannable which can be used for energy scan in GDA. It moves both hard X-ray ID gap and DCM energy")
ienergy_order = EnergyHarmonicOrder("ienergy_order")
I_FEEDBACK_PVS = ['BL09I-EA-FDBK-01:ENABLE','BL09I-EA-FDBK-02:ENABLE'] if installation.isLive() else None
ienergy_s = HardEnergy("ienergy_s", ienergy_order, igap, dcmenergy, "IIDCalibrationTable.txt", gap_offset = igap_offset, feedbackPVs = I_FEEDBACK_PVS)  # @UndefinedVariable
print("")
