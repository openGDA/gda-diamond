'''
Created on 20 Oct 2025

@author: fy65
'''

#beam metadata scannables
from gdascripts.scannable.beam.beamDivergence import BeamDivergence
dcm_beam_divergence_at_sample = BeamDivergence("dcm_beam_divergence_at_sample", horizontal = 3.3, vertical = 4.9)
from gdascripts.scannable.beam.beamFlux import BeamFlux
dcm_beam_flux_at_sample = BeamFlux("dcm_beam_flux_at_sample", flux = 0.0)
from gdascripts.scannable.beam.beamExtent import BeamExtent
dcm_beam_size_at_sample =  BeamExtent("dcm_beam_size_at_sample", horizontal_size = 6.0, vertical_size = 10.0)