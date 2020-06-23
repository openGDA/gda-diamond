from scannable.stats_monitor import NDStatsMonitor

print "---------------------------------------------------------"
print("Creating GigE cam stats objects")

d1camstats = NDStatsMonitor('d1camstats', d1cam_det_stat)
d1acamstats = NDStatsMonitor('d1acamstats', d1acam_det_stat)
d4camstats = NDStatsMonitor('d4camstats', d4cam_det_stat)
dcam1stats = NDStatsMonitor('dcam1stats', dcam1_det_stat)
dcam2stats = NDStatsMonitor('dcam2stats', dcam2_det_stat)
dcam3stats = NDStatsMonitor('dcam3stats', dcam3_det_stat)
dcam4stats = NDStatsMonitor('dcam4stats', dcam4_det_stat)
dcam5stats = NDStatsMonitor('dcam5stats', dcam5_det_stat)
dcam6stats = NDStatsMonitor('dcam6stats', dcam6_det_stat)
dcam7stats = NDStatsMonitor('dcam7stats', dcam7_det_stat)
dcam8stats = NDStatsMonitor('dcam8stats', dcam8_det_stat)

xrayeyestats = NDStatsMonitor('xrayeyestats', xrayeye_det_stat)
