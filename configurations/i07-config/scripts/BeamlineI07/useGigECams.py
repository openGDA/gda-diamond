from Diamond.AreaDetector.NdArrayPluginDevice import NdArrayWithStatPluginDeviceClass

print "---------------------------------------------------------"
print("Use xraycamstats for the Stats plugin of xraycam")

xrayeyestats = NdArrayWithStatPluginDeviceClass('xrayeyestats', xrayeye_det)
dcam8stats = NdArrayWithStatPluginDeviceClass('dcam8stats', dcam8_det)
