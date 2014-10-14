#init_2d_function_gen_scan.py
import pd_toggleBinaryPvDuringScan
import mtscripts.scannable.scaler
# TODO: Move to using mtscripts.scannable.waveform_channel once it supports raster scanning.

reload(pd_toggleBinaryPvDuringScan)
reload(mtscripts.scannable.scaler)

bo1enable = pd_toggleBinaryPvDuringScan.ToggleBinaryPvDuringScan('bo1enable', 'BL16B-EA-DIO-01:BO1', True, leave_at_end=True)
bo1enable.level = 100

mcs_controller = mtscripts.scannable.scaler.McsController(
    "BL16B-EA-DET-01:MCA-01:", internal_channel_advance=True)

mcs1 = mtscripts.scannable.scaler.McsChannelScannable('mcs1', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 1, new_collection_per_line=False)

mcs_y = mtscripts.scannable.scaler.McsChannelScannable('mcs_y', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 31, new_collection_per_line=False )

mcs_x = mtscripts.scannable.scaler.McsChannelScannable('mcs_x', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 27, new_collection_per_line=False )

mcs_apd = mtscripts.scannable.scaler.McsChannelScannable('mcs_apd', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 2, new_collection_per_line=False )
