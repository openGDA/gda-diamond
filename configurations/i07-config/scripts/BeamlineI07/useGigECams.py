from Diamond.AreaDetector.NdArrayPluginDevice import NdArrayWithStatPluginDeviceClass

print "---------------------------------------------------------"
print("Creating GigE cam stats objects")

d1camstats = NdArrayWithStatPluginDeviceClass('d1camstats', d1cam_det_stat)
d1acamstats = NdArrayWithStatPluginDeviceClass('d1acamstats', d1acam_det_stat)
d4camstats = NdArrayWithStatPluginDeviceClass('d4camstats', d4cam_det_stat)
dcam1stats = NdArrayWithStatPluginDeviceClass('dcam1stats', dcam1_det_stat)
dcam2stats = NdArrayWithStatPluginDeviceClass('dcam2stats', dcam2_det_stat)
dcam3stats = NdArrayWithStatPluginDeviceClass('dcam3stats', dcam3_det_stat)
dcam4stats = NdArrayWithStatPluginDeviceClass('dcam4stats', dcam4_det_stat)
dcam5stats = NdArrayWithStatPluginDeviceClass('dcam5stats', dcam5_det_stat)
dcam6stats = NdArrayWithStatPluginDeviceClass('dcam6stats', dcam6_det_stat)
dcam7stats = NdArrayWithStatPluginDeviceClass('dcam7stats', dcam7_det_stat)
dcam8stats = NdArrayWithStatPluginDeviceClass('dcam8stats', dcam8_det_stat)

xrayeyestats = NdArrayWithStatPluginDeviceClass('xrayeyestats', xrayeye_det_stat)
