#init_2d_function_gen_scan.py
import pd_toggleBinaryPvDuringScan
import scannable.hw.scaler
# TODO: Move to using mtscripts.scannable.waveform_channel once it supports raster scanning.

reload(pd_toggleBinaryPvDuringScan)
reload(scannable.hw.scaler)

bo1enable = pd_toggleBinaryPvDuringScan.ToggleBinaryPvDuringScan('bo1enable', 'BL16B-EA-DIO-01:BO1', True, leave_at_end=True)
bo1enable.level = 100

mcs_controller = scannable.hw.scaler.McsController(
    "BL16B-EA-DET-01:MCA-01:", internal_channel_advance=True)

mcs1 = scannable.hw.scaler.McsChannelScannable('mcs1', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 1, new_collection_per_line=False)

mcs_y = scannable.hw.scaler.McsChannelScannable('mcs_y', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 31, new_collection_per_line=False )

mcs_x = scannable.hw.scaler.McsChannelScannable('mcs_x', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 27, new_collection_per_line=False )

mcs_apd = scannable.hw.scaler.McsChannelScannable('mcs_apd', mcs_controller, "BL16B-EA-DET-01:MCA-01:", 2, new_collection_per_line=False )
