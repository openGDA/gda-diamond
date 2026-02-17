from gdascripts.mscanHandler import *
from uk.ac.gda.analysis.mscan import HklAdapter
from gda.configuration.properties import LocalProperties
from uk.ac.diamond.osgi.services import ServiceProvider
from org.eclipse.scanning.api.device import IRunnableDeviceService
from diffcalc.util import DiffcalcException
from gdascripts.metadata.metadata_commands import meta_add

ird_service = ServiceProvider.getService(IRunnableDeviceService)

#Default diff mode is eh1h
exc_name = "BL07I-ML-SCAN-01"
exs_name = "BL07I-ML-SCAN-11"
p2c_name = "BL07I-ML-SCAN-02"

if LocalProperties.get('gda.active.diffractometer.mode')=='eh1v' :
    exc_name = "BL07I-ML-SCAN-21"
    p2c_name = "BL07I-ML-SCAN-22"
elif LocalProperties.get('gda.active.diffractometer.mode')=='eh2' :
    exc_name = "BL07I-ML-SCAN-36"
    exs_name = "BL07I-ML-SCAN-36"

# Excalibur
exc = ird_service.getRunnableDevice(exc_name)
# Excalibur for static malcolm scans (i.e. "mscan static [parameters]") - avoids bug I07-569 but cannot move motors
exs = ird_service.getRunnableDevice(exs_name)
# Pilatus 2M
p2c = ird_service.getRunnableDevice(p2c_name)
# Pilatus 2M for static malcolm scans
p2s = ird_service.getRunnableDevice("BL07I-ML-SCAN-12")
# Eiger
eic = ird_service.getRunnableDevice("BL07I-ML-SCAN-03")
# Exc and p2m
m3 = ird_service.getRunnableDevice("BL07I-ML-SCAN-04")
# Pilatus 3
p3c = ird_service.getRunnableDevice("BL07I-ML-SCAN-35")
# Pilatus 3 for static malcolm scans
p3s = ird_service.getRunnableDevice("BL07I-ML-SCAN-32")

from BeamlineI07.i07_fscan import fscan, fpscan, fhklscan, cfscan
alias("fscan")
alias("fpscan")
alias("fhklscan")
alias("cfscan")

class DCHklAdapter(HklAdapter):
# eh1h: '_fourc', (diff1delta, diff1gamma, diff1chi, diff1theta)
    def getHkl(self, positions):
        try:
            return hkl._diffcalc.angles_to_hkl(positions)[0]
        except DiffcalcException:
            print("Error Calculating hkl - have you defined a UB matrix?")
            raise

    def getCurrentAnglePositions(self):
        return {scn_name:scn_pos for scn_name, scn_pos in zip(_fourc.getGroupMemberNames(), _fourc.getPosition())}

    def getFourCNames(self):
        return list(_fourc.getGroupMemberNames())

try:
    hkl_prov = DCHklAdapter()
    exc.setHklProvider(hkl_prov)
    exs.setHklProvider(hkl_prov)
    p2c.setHklProvider(hkl_prov)
    p2s.setHklProvider(hkl_prov)
    p3c.setHklProvider(hkl_prov)
    p3s.setHklProvider(hkl_prov)
except Exception as e:
    print("Error setting up hkl providers", e)

# ROI def meta recorder for dat
try:
    from roi_dat_meta import RoiMetaDatFileDevice
    ex_rois = RoiMetaDatFileDevice("ex_rois", "excalibur", "Excalibur")
    meta_add(ex_rois)
    p2_rois = RoiMetaDatFileDevice("p2_rois", "pilatus2", "Pilatus 2")
    meta_add(p2_rois)
    p3_rois = RoiMetaDatFileDevice("p3_rois", "pilatus3", "Pilatus 3")
    meta_add(p3_rois)
except Exception as e:
    print("Error setting up ROI meta devices", e)
