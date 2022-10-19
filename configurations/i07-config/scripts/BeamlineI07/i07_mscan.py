from gdascripts.mscanHandler import *
from uk.ac.gda.analysis.mscan import HklAdapter
from gda.factory import Finder

# Excalibur
exc = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
# Pilatus 2M
p2c = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-02")
# Exc and p2m
m3 = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-03")
# Pilatus 3
p3c = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-33")

from BeamlineI07.i07_fscan import fscan, fpscan, fhklscan, cfscan
alias(fscan)
alias(fpscan)
alias(fhklscan)
alias(cfscan)

class DCHklAdapter(HklAdapter):
# eh1h: '_fourc', (diff1delta, diff1gamma, diff1chi, diff1theta)
    def getHkl(self, positions):
        return hkl._diffcalc.angles_to_hkl(positions)[0]

    def getCurrentAnglePositions(self):
        return {scn_name:scn_pos for scn_name, scn_pos in zip(_fourc.getGroupMemberNames(), _fourc.getPosition())}

    def getFourCNames(self):
        return list(_fourc.getGroupMemberNames())

hkl_prov = DCHklAdapter()
exc.setHklProvider(hkl_prov)
p2c.setHklProvider(hkl_prov)
p3c.setHklProvider(hkl_prov)

# Inject normaliser processor for use in namespace
excalibur_norm = Finder.find("excalibur_norm")
#####

# PVA snapper
try:
    from exc_p import ExcPvaSnapper
    exc_snap = ExcPvaSnapper("exc_snap", exc_pva.getCollectionStrategy(),exc_pva.getAdditionalPluginList()[0].getNdPva(), Finder.find("excalibur_stats_verbose"))
except Exception as e:
    print("Error setting up exc snapper", e)
#####

# Exc Threshold
try:
    from exc_p import ExcThreshold
    excthresh = ExcThreshold("excthresh", excalibur.getController().getBasePv())
except Exception as e:
    print("Error setting up exc threshold", e)
#####

# ROI def meta recorder for dat
try:
    from roi_dat_meta import RoiMetaDatFileDevice
    ex_rois = RoiMetaDatFileDevice("ex_rois", "excalibur", ["exr", "exv"], "Excalibur")
    meta_add(ex_rois)
    p1_rois = RoiMetaDatFileDevice("p1_rois", "pilatus1", ["p1r", "p1v"], "Pilatus 1")
    meta_add(p1_rois)
    p2_rois = RoiMetaDatFileDevice("p2_rois", "pilatus2", ["p2r", "p2v"], "Pilatus 2")
    meta_add(p2_rois)
    p3_rois = RoiMetaDatFileDevice("p3_rois", "pilatus3", ["p3r", "p3v"], "Pilatus 3")
    meta_add(p3_rois)
except Exception as e:
    print("Error setting up ROI meta devices", e)
#####
