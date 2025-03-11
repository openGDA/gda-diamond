from gdascripts import installation as installation
from i09shared.pseudodevices.idgap_offset import IDGapOffset

from i09shared.scannable.energyHarmonicOrder import EnergyHarmonicOrder
from i09_2_shared.calibration.energy_polarisation_class import BeamEnergyPolarisationClass

from gdaserver import pgmenergy, jidscannable #@UnresolvedImport

print("-"*100)
print("Create an 'jenergy_s', 'polarisation' and 'jenergypolarisation' scannables.")
LH, LV, CR, CL, LH3 = ["LH","LV","CR","CL","LH3"]

jenergy_order = EnergyHarmonicOrder("jenergy_order")
jgap_offset = IDGapOffset("jgap_offset")
lookup_table = "JIDEnergy2GapCalibrations.csv"
jfeedbackPV = 'BL09J-EA-FDBK-01:ENABLE' if installation.isLive() else None

jenergy_s = BeamEnergyPolarisationClass("jenergy_s", jenergy_order, jidscannable, pgmenergy, lut=lookup_table, polarisationConstant=True, gap_offset=jgap_offset, feedbackPV=jfeedbackPV)
jenergy_s.configure()

polarisation = BeamEnergyPolarisationClass("polarisation", jenergy_order, jidscannable, pgmenergy, lut=lookup_table, energyConstant=True, gap_offset=jgap_offset, feedbackPV=jfeedbackPV)
polarisation.configure()

jenergypolarisation = BeamEnergyPolarisationClass("jenergypolarisation", jenergy_order, jidscannable, pgmenergy, lut=lookup_table, gap_offset=jgap_offset, feedbackPV=jfeedbackPV)
jenergypolarisation.configure()
jenergypolarisation.setInputNames(["jenergy"])
jenergypolarisation.setExtraNames(["polarisation"])

#I09-505
import sys
from i09shared.utils.ExceptionLogs import localStation_exception
try:
    print("Synchronising polarisation with hardware...")
    print("Initial ID polarisation is: " + polarisation.rawGetPosition())
except:
    localStation_exception(sys.exc_info(), "getting polarisation initial position")
print("")