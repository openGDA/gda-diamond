from Diamond.AreaDetector.NdArrayPluginDevice import NdArrayWithStatPluginDeviceClass

print "---------------------------------------------------------"
print("Creating GigE cam stats objects")

d1camstats = NdArrayWithStatPluginDeviceClass('d1camstats', d1cam_det)
d1acamstats = NdArrayWithStatPluginDeviceClass('d1acamstats', d1acam_det)
d4camstats = NdArrayWithStatPluginDeviceClass('d4camstats', d4cam_det)
dcam1stats = NdArrayWithStatPluginDeviceClass('dcam1stats', dcam1_det)
dcam2stats = NdArrayWithStatPluginDeviceClass('dcam2stats', dcam2_det)
dcam3stats = NdArrayWithStatPluginDeviceClass('dcam3stats', dcam3_det)
dcam4stats = NdArrayWithStatPluginDeviceClass('dcam4stats', dcam4_det)
dcam5stats = NdArrayWithStatPluginDeviceClass('dcam5stats', dcam5_det)
dcam6stats = NdArrayWithStatPluginDeviceClass('dcam6stats', dcam6_det)
dcam7stats = NdArrayWithStatPluginDeviceClass('dcam7stats', dcam7_det)
dcam8stats = NdArrayWithStatPluginDeviceClass('dcam8stats', dcam8_det)

xrayeyestats = NdArrayWithStatPluginDeviceClass('xrayeyestats', xrayeye_det)
