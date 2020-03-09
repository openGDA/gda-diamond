from gda.device.frelon.Frelon import InputChannels, ImageMode
from gda.device.lima.impl import LimaROIIntImpl
from gda.device.lima import LimaCCD
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from org.eclipse.january.dataset import DatasetFactory

def setDetectorRoiDefaults() :
    setDetectorRoi(64, 1984)

def setDetectorRoi(verticalBinning, verticalStart) :
    fr = frelon.getFrelon()
    # set roi_bin_offset to 0 otherwise might get problem setting new ROI if value is inconsistent with ROI...
    fr.setROIBinOffset(0)
    ## Set the parameters on FrelonCcdDetector data object...
    ccdConfig = frelon.getDetectorData()
    ## CcdBeginLine, verticalBinValue, areaOfInterest are set in call to configureDetectorForROI(...)
    #ccdConfig.setCcdBeginLine(1984)
    #ccdConfig.setVerticalBinValue(64)
    #ccdConfig.setAreaOfInterest(LimaROIIntImpl(0, 31, 2048, 1))
    ccdConfig.setSpb2Config(fr.SPB2Config.SPEED)
    ccdConfig.setRoiMode(fr.ROIMode.KINETIC)
    # ccdConfig.setImageMode(ImageMode.FRAME_TRANSFER) # this is for 'half ccd' image modes
    ccdConfig.setImageMode(ImageMode.FULL_FRAME)
    ccdConfig.setInputChannel(InputChannels.I3_4)

    ## Apply the above settings to detector and set the ROI based on vertical binning size and vertical pixel to readout :
    frelon.configureDetectorForROI(verticalBinning, verticalStart) # vertical binning, vertical pixel
    # roi_bin_offset=vertical pixel%vertical binning;

# Can also apply settings directly on detector using frelon and limaCcd objects :
def setDetectorRoiDirectly(verticalBinning, verticalStart) :

    fr = frelon.getFrelon()
    ccd = frelon.getLimaCcd()

    ## Set to zero initially so it's always consistent with settings for new ROI
    fr.setROIBinOffset(0)

    # Set image mode to use frame transfer (image_mode)
    fr.setImageMode(ImageMode.FULL_FRAME)
    # fr.setImageMode(ImageMode.FRAME_TRANSFER)

    # Set kinetic ROI readout mode (roi_mode)
    fr.setROIMode(fr.ROIMode.KINETIC)

    # Set to use 'speed' image mode  (spb2_config)
    fr.setSPB2Config(fr.SPB2Config.SPEED)

    # Set quadrants 3,4 (input_channel)
    fr.setInputChannels(InputChannels.I3_4)

    # Bin size of 64 in vertical direction
    ccd.setImageBin(1, verticalBinning)

    # Set ROI window (sizes in units of the binning). Last row of pixels.
    # ystart = ypixel / ybinning = 1984 / 64 = 31
    ystart = verticalStart / verticalBinning
    ccd.setImageROIInt(LimaROIIntImpl(0, ystart, 2048, 1)) # xstart, ystart, xsize, ysize

    # Set kinetic roi offset (roi_bin_offset). This is the vertical offset of pixel row within the ROI to readout
    # roi_bin_offset = verticalStart%verticalBinning = 1984%64 = 0
    offset = verticalStart%verticalBinning
    fr.setROIBinOffset(offset)

def setImageMode(exposureTime, numFrames) :
    fr = frelon.getFrelon()
    ccd = frelon.getLimaCcd()

    ## Set to zero initially so it's always consistent with settings for new ROI
    fr.setROIBinOffset(0)

    # Set image mode to use frame transfer (image_mode)
    fr.setImageMode(ImageMode.FULL_FRAME)

    # Set to use 'speed' image mode  (spb2_config)
    fr.setSPB2Config(fr.SPB2Config.SPEED)

    # Set quadrants 3,4 (input_channel)
    fr.setInputChannels(InputChannels.I3_4)

    # Bin size of 64 in vertical direction
    ccd.setImageBin(1, 1)

    ccd.setImageROIInt(LimaROIIntImpl(0, 0, 2048, 2048)) # xstart, ystart, xsize, ysize

    ccd.setAcqMode(LimaCCD.AcqMode.SINGLE)

    ccd.setAcqTriggerMode(LimaCCD.AcqTriggerMode.INTERNAL_TRIGGER)

    ccd.setAcqExpoTime(exposureTime)

    ccd.setAcqNbFrames(numFrames)

def collectImage() :
    ccd = frelon.getLimaCcd()
    ccd.stopAcq()
    sleep(0.1)
    ccd.prepareAcq()
    sleep(0.1)    
    ccd.startAcq()

def getNumAvailableImages() :
    return frelon.getLimaCcd().getLastImageReady()

def plotImage(imageNumber) :
    print "Plotting image %d of %d"%(imageNumber, getNumAvailableImages())
    image1=frelon.readoutFrames(imageNumber, imageNumber)
    dat=DatasetFactory.createFromObject(image1, 2048, 2048)
    # dnp.plot.image(dat, name="frelon image")
    yAxisValues = DatasetFactory.createFromObject(range(0,2048))
    xAxisValues = DatasetFactory.createFromObject(range(0,2048))
    SDAPlotter.imagePlot("frelon image", xAxisValues, yAxisValues, dat)

def collectSingleImageInLoop(exposureTime) :

    setImageMode(exposureTime, 1)
    firstTime = True
    while True :
        collectImage()
        sleep(1.5)
        plotImage(0)

def waitForImage(imageToWaitFor) :
    availableImages = getNumAvailableImages()
    print "Waiting for image %d - %d available"%(imageToWaitFor, availableImages)
    if availableImages >= imageToWaitFor :
        return

    while getNumAvailableImages() < imageToWaitFor :
        sleep(0.001)

def collectImageInLoop(exposureTime, numFrames) :

    setImageMode(exposureTime, numFrames)
    firstTime = True
    collectImage()
    for i in range(numFrames) :
        waitForImage(i)
        plotImage(i)

print "Functions from frelon02-kinetic-roi-settings.py : "
print "    Set detector ROI (kinetic ROI mode) : setDetectorRoi(verticalBinning, verticalStart)"
print "    Collect several images in loop : collectImageInLoop(exposureTime, numFrames)  "
print "    Collect image in infinte loop  : collectSingleImageInLoop(exposureTime)"
