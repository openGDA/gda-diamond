
from Diamond.PseudoDevices.Scaler8512DirectPV import ScalerChannelEpicsPVClass;

pvScalerRoot="ME02P-EA-DET-01:SCALER";
pvScalerTP = pvScalerRoot +":PRESET";

pvScalerCNT=pvScalerRoot + ":STARTCOUNT";

pvCA01C = pvScalerRoot + ":CH1";
pvCA02C = pvScalerRoot + ":CH2";
pvCA03C = pvScalerRoot + ":CH3";
pvCA04C = pvScalerRoot + ":CH4";
pvCA05C = pvScalerRoot + ":CH5";
pvCA06C = pvScalerRoot + ":CH6";
pvCA07C = pvScalerRoot + ":CH7";
pvCA08C = pvScalerRoot + ":CH8";


#Use the scaler "scaled" count
ca01s = ScalerChannelEpicsPVClass("ca01s",pvScalerTP, pvScalerCNT, pvCA01C);
ca02s = ScalerChannelEpicsPVClass("ca02s",pvScalerTP, pvScalerCNT, pvCA02C);
ca03s = ScalerChannelEpicsPVClass("ca03s",pvScalerTP, pvScalerCNT, pvCA03C);
ca04s = ScalerChannelEpicsPVClass("ca04s",pvScalerTP, pvScalerCNT, pvCA04C);
ca05s = ScalerChannelEpicsPVClass("ca05s",pvScalerTP, pvScalerCNT, pvCA05C);
ca06s = ScalerChannelEpicsPVClass("ca06s",pvScalerTP, pvScalerCNT, pvCA06C);
ca07s = ScalerChannelEpicsPVClass("ca07s",pvScalerTP, pvScalerCNT, pvCA07C);
ca08s = ScalerChannelEpicsPVClass("ca08s",pvScalerTP, pvScalerCNT, pvCA08C);


#Use the scaler Raw count
pvCA01CRAW = pvScalerRoot + ":CH1-RAW";
pvCA02CRAW = pvScalerRoot + ":CH2-RAW";
pvCA03CRAW = pvScalerRoot + ":CH3-RAW";
pvCA04CRAW = pvScalerRoot + ":CH4-RAW";
pvCA05CRAW = pvScalerRoot + ":CH5-RAW";
pvCA06CRAW = pvScalerRoot + ":CH6-RAW";
pvCA07CRAW = pvScalerRoot + ":CH7-RAW";
pvCA08CRAW = pvScalerRoot + ":CH8-RAW";


ca01sr = ScalerChannelEpicsPVClass("ca01sr",pvScalerTP, pvScalerCNT, pvCA01CRAW);
ca02sr = ScalerChannelEpicsPVClass("ca02sr",pvScalerTP, pvScalerCNT, pvCA02CRAW);
ca03sr = ScalerChannelEpicsPVClass("ca03sr",pvScalerTP, pvScalerCNT, pvCA03CRAW);
ca04sr = ScalerChannelEpicsPVClass("ca04sr",pvScalerTP, pvScalerCNT, pvCA04CRAW);
ca05sr = ScalerChannelEpicsPVClass("ca05sr",pvScalerTP, pvScalerCNT, pvCA05CRAW);
ca06sr = ScalerChannelEpicsPVClass("ca06sr",pvScalerTP, pvScalerCNT, pvCA06CRAW);
ca07sr = ScalerChannelEpicsPVClass("ca07sr",pvScalerTP, pvScalerCNT, pvCA07CRAW);
ca08sr = ScalerChannelEpicsPVClass("ca08sr",pvScalerTP, pvScalerCNT, pvCA08CRAW);
