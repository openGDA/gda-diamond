from gdascripts.mscanHandler import *
from uk.ac.gda.analysis.mscan import HklAdapter
from gda.factory import Finder

# Excalibur
exc = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-01")
# Pilatus 2M
p2c = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-02")
# Exc and p2m
m3 = getRunnableDeviceService().getRunnableDevice("BL07I-ML-SCAN-03")


from BeamlineI07.i07_fscan import fscan, fpscan
alias(fscan)
alias(fpscan)

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

# Exc filename recorder
try:
    from exc_h5_meta import ExcaliburExtFileMeta
    excalibur_h5_data = ExcaliburExtFileMeta("excalibur_h5_data", "excalibur", ["excalibur", "excroi", "excstats", "exc_p", "exr", "exv"])
    meta_add(excalibur_h5_data)
except Exception as e:
    print("Error setting up excalibur_h5_data", e)
#####

# Inject normaliser processor for use in namespace
excalibur_norm = Finder.find("excalibur_norm")
#####

# PVA snapper
try:
    from exc_p import ExcPvaSnapper
    exc_snap = ExcPvaSnapper("exc_snap", exc_pva.getCollectionStrategy(),exc_pva.getAdditionalPluginList()[0].getNdPva(), Finder.find("excalibur_stats_standard"))
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
