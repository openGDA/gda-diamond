from peem.leem_instances import leem_fov
from peem.LEEM2000_scannables_init import leem_rot
from gdaserver import m4fpitch, m5fpitch, pcotif, psphi
from beam.BeamStablisation_Class import BeamStabilisation, m4fpitchRead,\
    m5fpitchRead
from beam.AreaDetectorROIs import setupROIs, prepareROIsForCollection

#create ROIs in the format of [x_start, y_start, x_size, y_size]
roi1=[1, 1, 1000, 250]   #top
roi2=[750, 1, 250, 1000] #right
roi3=[1, 750, 1000, 250] #bottom
roi4=[1, 1, 250, 1000]   #left
rois=[roi1,roi2,roi3,roi4]

#push the rois to GDA server. Don't draw any ROI in LiveStreamView after the following statement being run, otherwise these rois will be override
setupROIs(rois)
#push the rois and corresponding stats to EPICS area detector
prepareROIsForCollection(pcotif,1) #replace 'pcotif' with 'pco' to produce nexus file
    
####declaration
cb = BeamStabilisation(rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi)
cb.maxError = 0.01

storeBeamPosition=cb.storeBeamPos()
centerBeam=cb.centerBeamSingle(False)
