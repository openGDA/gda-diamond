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
from gdascripts.utils import caput

exposure_limited_cs = ExposureLimitedCollectionStrategy("exposure_limited_cs", andor, fastshutter, exposure_time_limit = 0.1, motors = [y,z], beam_size = None, sample_size = None, sample_centre = None)
#please ensure you update motor speed limits for the motor you are using for raster scanning!
exposure_limited_cs.setZMaxSpeed(0.5)
exposure_limited_cs.setZMinSpeed(0.0)
exposure_limited_cs.setYMaxSpeed(0.5)
exposure_limited_cs.setYMinSpeed(0.0)
exposure_limited_cs.setUseSampleSize(False)

#filter out collection strategy
additional_plugins = [plugin for plugin in andor.getAdditionalPluginList() if not isinstance(plugin, NXCollectionStrategyPlugin)]

el_andor = ExposureLimitedDetector("el_andor", exposure_limited_cs, additional_plugins)
el_andor.setAddCollectTimeMs(True)

el_andor.setBeamSize([0.030, 0.005])

# use sample size and centre
# el_andor.setSampleSize([0.2, 7.7])
# el_andor.setSampleCentre([3.2,0.35])

# use sample start and end
el_andor.setSampleStart([1.0, 2.0])
el_andor.setSampleEnd([3.0, 4.0])

el_andor.setExposureTimeLimit(0.1)
el_andor.setYContinuous(False)
el_andor.setZContinuous(True)
el_andor.setYStep(0.030)
el_andor.setZStep(0.005)
el_andor.setPathReverse(True)

    
# caput("BL21I-EA-SMPL-01:Z.BDST",0)
# # caput("BL21I-EA-SMPL-01:Z.VELO",0.05)
# # scan ds 1 10 1 el_andor 180
# caput("BL21I-EA-SMPL-01:Z.BDST",0.4)
# caput("BL21I-EA-SMPL-01:Z.VELO",0.15)