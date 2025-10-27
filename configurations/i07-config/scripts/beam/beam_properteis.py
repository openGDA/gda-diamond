'''
Created on 20 Oct 2025

@author: fy65
'''

#beam metadata scannables
from gdascripts.scannable.beam.beamDivergence import BeamDivergence
beam_divergence_at_sample = BeamDivergence("beam_divergence_at_sample", horizontal = 3.3, vertical = 4.9)
from gdascripts.scannable.beam.beamFlux import BeamFlux
beam_flux_at_sample = BeamFlux("beam_flux_at_sample", flux = 0.0)
from gdascripts.scannable.beam.beamExtent import BeamExtent
beam_size_at_sample =  BeamExtent("beam_size_at_sample", horizontal_size = 6.0, vertical_size = 10.0)