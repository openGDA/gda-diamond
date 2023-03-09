'''
Create 'el_andor' detector and associated collection strategy for sample position exposure limited experiment.
It ensures the X-ray beam illumination time at every point on the sample does not over exposure limit set,
while the detector exposure time is set much longer, and within this time sample is continuous moving across the X-ray beam.
 
Created on Feb 13, 2023

@author: fy65
'''
from detectors.SnakeMotionAndShutterControlCollectionStrategy import ExposureLimitedCollectionStrategy
from gdaserver import andor, fastshutter, y, z  # @UnresolvedImport
from gda.device.detector.nxdetector import NXCollectionStrategyPlugin
from detectors.MotionCoupledDetector import ExposureLimitedDetector

exposure_limited_cs = ExposureLimitedCollectionStrategy("exposure_limited_cs", andor, fastshutter, exposure_time_limit = 0.1, motors = [y,z], beam_size = None, sample_size = None, sample_centre = None)

#filter out collection strategy
additional_plugins = [plugin for plugin in andor.getAdditionalPluginList() if not isinstance(plugin, NXCollectionStrategyPlugin)]

el_andor = ExposureLimitedDetector("el_andor", exposure_limited_cs, additional_plugins)
el_andor.setAddCollectTimeMs(True)

el_andor.setBeamSize([0.030, 0.005])
#el_andor.setSampleSize([6.2, 7.7])
el_andor.setSampleSize([0.2, 7.7])
#el_andor.setSampleCentre([-0.3,0.35])
el_andor.setSampleCentre([-3.2,0.35])
el_andor.setExposureTimeLimit(0.1)
el_andor.setYContinuous(False)
el_andor.setZContinuous(True)
el_andor.setYStep(0.030)
el_andor.setZStep(0.005)
el_andor.setPathReverse(True)
