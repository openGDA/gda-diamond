import i09shared.installation as installation
from calibration.hard_energy_class import HardEnergy
from pseudodevices.IDGap_Offset import igap_offset, jgap_offset
from scannable.energyHarmonicOrder import EnergyHarmonicOrder
from i09shared.calibration.energy_polarisation_class import BeamEnergyPolarisationClass

from gdaserver import igap, dcmenergy, pgmenergy, jidscannable # @UnresolvedImport

print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'ienergy_s' scannable which can be used for energy scan in GDA. It moves both hard X-ray ID gap and DCM energy"
ienergy_order = EnergyHarmonicOrder("ienergy_order")
if installation.isLive():
    ienergy_s = HardEnergy("ienergy_s", ienergy_order, igap, dcmenergy, "IIDCalibrationTable.txt",gap_offset=igap_offset, feedbackPVs=['BL09I-EA-FDBK-01:ENABLE','BL09I-EA-FDBK-02:ENABLE'])  # @UndefinedVariable
else:
    ienergy_s = HardEnergy("ienergy_s", ienergy_order, igap, dcmenergy,"IIDCalibrationTable.txt", gap_offset=igap_offset, feedbackPVs=None)  # @UndefinedVariable
    
print
print "-----------------------------------------------------------------------------------------------------------------"

print "Create an 'jenergy_s', 'polarisation' and 'jenergypolarisation' scannables."
LH,LV,CR,CL,LH3=["LH","LV","CR","CL","LH3"]
jenergy_order = EnergyHarmonicOrder("jenergy_order")
if installation.isLive():
    jenergy_s=BeamEnergyPolarisationClass("jenergy_s", jenergy_order, jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", polarisationConstant=True, gap_offset=jgap_offset, feedbackPV='BL09J-EA-FDBK-01:ENABLE')  # @UndefinedVariable
    polarisation=BeamEnergyPolarisationClass("polarisation", jenergy_order, jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", energyConstant=True, gap_offset=jgap_offset, feedbackPV='BL09J-EA-FDBK-01:ENABLE')  # @UndefinedVariable
    jenergypolarisation=BeamEnergyPolarisationClass("jenergypolarisation", jenergy_order, jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", gap_offset=jgap_offset, feedbackPV='BL09J-EA-FDBK-01:ENABLE')  # @UndefinedVariable
else:
    jenergy_s=BeamEnergyPolarisationClass("jenergy_s", jenergy_order, jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", polarisationConstant=True, gap_offset=jgap_offset, feedbackPV=None)  # @UndefinedVariable
    polarisation=BeamEnergyPolarisationClass("polarisation", jenergy_order, jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", energyConstant=True, gap_offset=jgap_offset, feedbackPV=None)  # @UndefinedVariable
    jenergypolarisation=BeamEnergyPolarisationClass("jenergypolarisation", jenergy_order, jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.csv", gap_offset=jgap_offset, feedbackPV=None)  # @UndefinedVariable

jenergy_s.configure()
polarisation.configure()
jenergypolarisation.configure()
jenergypolarisation.setInputNames(["jenergy"])
jenergypolarisation.setExtraNames(["polarisation"])

#I09-505
print("")
print("Synchronising polarisation with hardware...")
print("Initial ID polarisation is: " + polarisation.rawGetPosition())

print "-----------------------------------------------------------------------------------------------------------------"

#Connect the JythonScannableWrappers
from gdaserver import ienergy_order_wrapper, jenergy_order_wrapper, igap_offset_wrapper, jgap_offset_wrapper, polarisation_wrapper # @UnresolvedImport
ienergy_order_wrapper.connectScannable()
jenergy_order_wrapper.connectScannable()
igap_offset_wrapper.connectScannable()
jgap_offset_wrapper.connectScannable()
polarisation_wrapper.connectScannable()
