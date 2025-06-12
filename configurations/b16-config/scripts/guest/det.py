from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from det_wrapper.DetectorDataProcessorForNexus import DetectorDataProcessorWithRoiForNexus
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.PixelIntensity import PixelIntensity

def hamamatsu():
    global hamamatsu, hamapeak2d, hamamax2d, hamaintensity2d
    from gdaserver import hama_tif  # @UnresolvedImport
    
    hama_tif.configure()
    
    hamamatsu = SwitchableHardwareTriggerableProcessingDetectorWrapper('hamamatsu', hama_tif, None, hama_tif, [], panel_name_rcp='hamamatsu', returnPathAsImageNumberOnly=True, fileLoadTimout=60)
    hamapeak2d = DetectorDataProcessorWithRoiForNexus('hamapeak2d', hamamatsu, [TwodGaussianPeak()])
    hamamax2d = DetectorDataProcessorWithRoiForNexus('hamamax2d', hamamatsu, [SumMaxPositionAndValue()])
    hamaintensity2d = DetectorDataProcessorWithRoiForNexus('hamaintensity2d', hamamatsu, [PixelIntensity()])
    
    print("Created detector %s, and processors %s, %s, and %s" % (hamamatsu.name, hamapeak2d.name, hamamax2d.name, hamaintensity2d.name))