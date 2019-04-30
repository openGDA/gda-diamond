from peem.leem_instances import leem_fov
from peem.LEEM2000_scannables_init import leem_rot
from gdaserver import m4fpitch, m5fpitch, pcotif, psphi
from beam.BeamStablisation_Class import m4fpitchRead, m5fpitchRead, BeamStablisationUsingAreaDetectorRoiStatPair, BeamStablisationUsingExtraRoiStatPair

# create ROIs in the format of [x_start, y_start, x_size, y_size]
roi1 = [1, 1, 1000, 250]  # top
roi2 = [750, 1, 250, 1000]  # right
roi3 = [1, 750, 1000, 250]  # bottom
roi4 = [1, 1, 250, 1000]  # left
rois = [roi1, roi2, roi3, roi4]

# use 1st 4 ROI-STAT pair from detector pcotif or pco
#cb = BeamStablisationUsingAreaDetectorRoiStatPair(rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index=[1, 2, 3, 4], pvRootName="BL06I-EA-DET-01", detector=pcotif, roi_provider_name="pco_roi")
# use extra 4 ROI-STAT pair from ROTATED image
cb = BeamStablisationUsingExtraRoiStatPair(rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index=[7, 8, 9, 10], pvRootName="BL06I-EA-DET-01")

cb.maxError = 0.01

storeBeamPosition = cb.storeBeamPos()
centerBeam = cb.centerBeamAuto(False)
