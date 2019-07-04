from gda.device.detector.areadetector import EpicsAreaDetector
AreaDetector = EpicsAreaDetector()
AreaDetector.setBasePVName("BL06I-EA-PIXIS-01:CAM:")
AreaDetector.setInitialDataType("UInt16")
AreaDetector.setInitialMinX(0)
AreaDetector.setInitialMinY(0)
AreaDetector.setInitialSizeX(2048)
AreaDetector.setInitialSizeY(2048)
AreaDetector.setInitialBinX(1)
AreaDetector.setInitialBinY(1)
AreaDetector.configure()

from gda.device.detector.areadetector import EpicsAreaDetectorFileSave
FullFrameFileSave = EpicsAreaDetectorFileSave()
FullFrameFileSave.setBasePVName("BL06I-EA-PIXIS-01:TIFF1:")
FullFrameFileSave.setInitialFileName("pixis")
FullFrameFileSave.setInitialFileTemplate("%s/%s_%06d.tif")
FullFrameFileSave.setInitialAutoIncrement("Yes")
FullFrameFileSave.setInitialAutoSave("Yes")
FullFrameFileSave.setInitialWriteMode("Single")
FullFrameFileSave.setInitialNumCapture(99999)
FullFrameFileSave.setInitialArrayPort("PVCAM")
FullFrameFileSave.setInitialArrayAddress(0)
FullFrameFileSave.configure()

from gda.device.detector.areadetector import EPICSAreaDetectorImage
ImageArray =EPICSAreaDetectorImage()
ImageArray.setBasePVName("BL06I-EA-PIXIS-01:IMAGE1:")
ImageArray.setInitialArrayPort("PVCAM")
ImageArray.setInitialArrayAddress("0")
ImageArray.configure()

from gda.device.detector.areadetector import EpicsAreaDetectorROI
AreaDetectorROI = EpicsAreaDetectorROI()
AreaDetectorROI.setBasePVName("BL06I-EA-PIXIS-01:ROI1:")
AreaDetectorROI.configure()

from gda.device.detector.pixis import PixisController
pixis = PixisController()
pixis.setAreaDetector(AreaDetector)
pixis.setFullFrameSaver(FullFrameFileSave)
pixis.setImage(ImageArray)
pixis.setAreaDetectorROI(AreaDetectorROI)
pixis.setIdlePollTime_ms(100)
pixis.setName("pixis")
pixis.configure()
