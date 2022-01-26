from Diamond.BimorphMirror.BimorphVoltageDevice import BimorphVoltageDeviceClass;

print "initialise HFM / VFM bimorph mirror devices"
#HFM Bimorph voltage channels: 0-7,  PVs: BL07I-OP-KBM-01:HFM:SET-VOUT00 - BL07I-OP-KBM-01:HFM:SET-VOUT07
#VFM Bimorph voltage channels: 0-15, PVs: BL07I-OP-KBM-01:VFM:SET-VOUT00 - BL07I-OP-KBM-01:VFM:SET-VOUT15

hfmBasePV = "BL07I-OP-KBM-01:HFM";
vfmBasePV = "BL07I-OP-KBM-01:VFM";

HFMVoltagePV = "BL07I-OP-KBM-01:HFM:SET-VOUT";
HFMMonitorPV = "BL07I-OP-KBM-01:HFM:GET-VOUT";
HFMStatusPV = "BL07I-OP-KBM-01:HFM:GET-STATUS";

VFMVoltagePV = "BL07I-OP-KBM-01:VFM:SET-VOUT";
VFMMonitorPV = "BL07I-OP-KBM-01:VFM:GET-VOUT";
VFMStatusPV = "BL07I-OP-KBM-01:VFM:GET-STATUS";

hfm = BimorphVoltageDeviceClass('hfm', hfmBasePV, 8, 10);
vfm = BimorphVoltageDeviceClass('vfm', vfmBasePV, 16, 10, "BL07I-OP-KBM-01:HFM:GET-STATUS");


#Old bimorph voltage setter
from Diamond.BimorphMirror.BimorphVoltageSetter import HfmBm, VfmBm;

print "initialise HFM / VFM bimorph voltage setters"
hfmbm = HfmBm()
vfmbm = VfmBm()
print "hfmbm: " + str(hfmbm) + "vfmbm: " + str(vfmbm)
