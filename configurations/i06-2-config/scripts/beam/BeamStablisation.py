from peem.leem_scannables import leem_FOV_A, leem_rot
from gdaserver import medipix  # @UnresolvedImport
from beam.BeamStablisation_Class import m4fpitch, m5fpitch, BeamStablisationUsingAreaDetectorRoiStatPair, BeamStablisationUsingExtraRoiStatPair
from gda.device.scannable import DummyScannable

# create ROIs in the format of [x_start, y_start, x_size, y_size]
roi1 = [1, 1, 1000, 250]  # top
roi2 = [750, 1, 250, 1000]  # right
roi3 = [1, 750, 1000, 250]  # bottom
roi4 = [1, 1, 250, 1000]  # left
rois = [roi1, roi2, roi3, roi4]

#TODO replace this temporary scannable with real pschi motor
psphi = DummyScannable('psphi')

# use 1st 4 ROI-STAT pair from detector medipix
cb1 = BeamStablisationUsingAreaDetectorRoiStatPair(rois, leem_FOV_A, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index=[1, 2, 3, 4], pvRootName="BL06I-EA-DET-02", detector=medipix, roi_provider_name="medipix_roi")
cb1.max_error = 0.01
cb1_storeBeamPosition = cb1.store_beam_positions()
cb1_centerBeam = cb1.center_beam_auto(False)

# use extra 4 ROI-STAT pair from ROTATED image
cb = BeamStablisationUsingExtraRoiStatPair(rois, leem_FOV_A, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index=[7, 8, 9, 10], pv_root_name="BL06I-EA-DET-02")
cb.max_error = 0.01
storeBeamPosition = cb.store_beam_positions()
centerBeam = cb.center_beam_auto(False)
