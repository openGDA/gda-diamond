print "Running medipix_functions.py"

from gda.epics import CAClient

defaultDetector=medipix1


# Function for setting exposure time and setting continuous acquisition
# Called in ADControllerBase.setExposure(time) - see client side medipixADController bean
# (injected using setExposureTimeCmd )
def setMedipixExposureAndStart(exposureTime) :
    continuousModeIndex = 2 # ImageMode.CONTINUOUS.ordinal()
    adbase = medipix_addetector.getAdBase()

    adbase.setAcquireTime(exposureTime);
    adbase.setAcquirePeriod(0.0);
    adbase.setImageMode(continuousModeIndex);
    adbase.startAcquiring();

def getPluginsFromFindableObjectHolder(detectorObject):
    return Finder.find(detectorObject.getName()+"_plugins")

# Retrieve the NXdetector mutableROI plugin list for a medipix detector : 
def getMedipixMutableRoiPlugins(detectorObject):
    pluginHolder = getPluginsFromFindableObjectHolder(detectorObject)
    return pluginHolder.get("plugins_mutable_roi")

# Retrieve the NXdetector  plotserver ROI plugin list : 
def getMedipixPlotserverRoiPlugins(detectorObject):
    pluginHolder = getPluginsFromFindableObjectHolder(detectorObject)
    return pluginHolder.get("plugins_plotserver_roi")

# Retrieve the basePv name for a Medipix detector : 
def getMedipixBasePvName(detectorObject):
    pluginHolder = getPluginsFromFindableObjectHolder(detectorObject)
    return pluginHolder.get("basePvName")

def getMedipixMutableRoi(detectorObject):
    return Finder.find(detectorObject.getName()+"_roi")


# Find the the 2 'additional plugin' lists : one to  use ROI from plotserver and one to use mutable ROI
def setupMedipixPlugins(detectorObject=defaultDetector) :
    
    # Get the PV name and plotserver roi plugin object
    basePvName = getMedipixBasePvName(detectorObject)
    
    # Get plotserver roi plugin list object
    plotserverPlugins = getMedipixPlotserverRoiPlugins(detectorObject)

    # Set the initial plugin list on the detector
    detectorObject.setAdditionalPluginList(plotserverPlugins)
    
    #set array input port and callbacks for ARR plugin (so live stream works correctly)
    try :
        CAClient.put(basePvName+":ARR:EnableCallbacks", 1)
        CAClient.put(basePvName+":ARR:MinCallbackTime", 0)
        
        cam_port = CAClient.get(basePvName+":CAM:PortName_RBV")
        CAClient.put(basePvName+":ARR:NDArrayPort", cam_port)

    except (Exception, java.lang.Throwable) as err:
        print "Problem setting callbacks and array port for medipix :ARR plugin", err

def setUseMedipixRoiFromGui(useRoiFromGui, detectorObject=defaultDetector):
    plotserverRoiPlugins = getMedipixPlotserverRoiPlugins(detectorObject)
    mutableRoiPlugins = getMedipixMutableRoiPlugins(detectorObject)

    if useRoiFromGui :
        print "Using "+detectorObject.getName()+" ROI from GUI"
        detectorObject.setAdditionalPluginList(plotserverRoiPlugins)
    else :
        print "Using "+detectorObject.getName()+" ROI from Jython"
        detectorObject.setAdditionalPluginList(mutableRoiPlugins)

def setMedipixRoi(xstart, ystart, xsize, ysize, detectorObject=defaultDetector) :
    print "Setting "+detectorObject.getName()+" Jython ROI"
    mutableRoi = getMedipixMutableRoi(detectorObject)

    mutableRoi.setXstart(xstart)
    mutableRoi.setYstart(ystart)
    mutableRoi.setXsize(xsize)
    mutableRoi.setYsize(ysize)
    showMedipixRoi()

def showMedipixRoi(detectorObject=defaultDetector) :
    roi = getMedipixMutableRoi(detectorObject)
    print "Jython ROI for %s : start = (%d, %d), size = (%d, %d)"%(detectorObject.getName(), roi.getXstart(), roi.getYstart(),  roi.getXsize(), roi.getYsize())



setupMedipixPlugins(medipix1)
setupMedipixPlugins(medipix2)

medipix_roi = getMedipixMutableRoi(medipix1)
medipix2_roi = getMedipixMutableRoi(medipix2)

print "Set Medipix to use ROI from GUI : 'setUseMedipixRoiFromGui(True)'. Set to False to use ROI from Jython"
print "Set Medipix Jython ROI : 'setMedipixRoi(xstart, xsize, ystart, ysize)'"
print "Show Medipix Jython ROI : showMedipixRoi()"
print "Used medipix1 or medipix2 as the last parameter to choose a particular detector (e.g. showMedipixRoi(medipix2)) "
