from Diamond.BimorphVoltageSetter.BimorphVoltageSetter import HfmBm, VfmBm;
from Diamond.BimorphVoltageSetter.BimorphVoltageSetter import BimorphVoltageDevice;

print "initialise HFM / VFM bimorph voltage setters"
hfmbm = HfmBm();
vfmbm = VfmBm();
print "hfmbm: " + str(hfmbm) + "vfmbm: " + str(vfmbm);


HFMVoltagePV = "BL07I-OP-KBM-01:HFM:SET-VOUT";
HFMMonitorPV = "BL07I-OP-KBM-01:HFM:GET-VOUT";

VFMVoltagePV = "BL07I-OP-KBM-01:VFM:SET-VOUT"
VFMMonitorPV = "BL07I-OP-KBM-01:VFM:GET-VOUT"
	
#bm_hfm = BimorphVoltageDevice('hfm', HFMVoltagePV, HFMMonitorPV, 8, 300);
#bm_vfm = BimorphVoltageDevice('vfm', VFMVoltagePV, VFMMonitorPV, 16, 300);

