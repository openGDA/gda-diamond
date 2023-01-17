print "Running medipix_functions.py"

from gda.epics import CAClient

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
    medipix_plugins = getPluginsFromFindableObjectHolder(detectorObject)
    return medipix_plugins.get("plugins_mutable_roi")

# Retrieve the NXdetector  plotserver ROI plugin list : 
def getMedipixPlotserverRoiPlugins(detectorObject):
    medipix_plugins = getPluginsFromFindableObjectHolder(detectorObject)
    return medipix_plugins.get("plugins_plotserver_roi")

# Retrieve the basePv name for a Medipix detector : 
def getMedipixBasePvName(detectorObject):
    medipix_plugins = getPluginsFromFindableObjectHolder(detectorObject)
    return medipix_plugins.get("basePvName")

def getMedipixMutableRoi(detectorObject):
    return Finder.find(detectorObject.getName()+"_roi")


# Find the the 2 'additional plugin' lists : one to  use ROI from plotserver and one to use mutable ROI
def setupMedipixPlugins(detectorObject=medipix) :

    medipixNamePrefix = detectorObject.getName()
    
    #  Get the findable map containing the additional plugin lists
    medipix_plugins = Finder.find(medipixNamePrefix+"_plugins")

    # Get the two plugin lists
    plugins_plotserver_roi = medipix_plugins.get("plugins_plotserver_roi")
    medipix_basePvName = medipix_plugins.get("basePvName")

    # Set the initial plugin list on the detector
    medipix.setAdditionalPluginList(plugins_plotserver_roi)
    
    #set array input port and callbacks for ARR plugin (so live stream works correctly)
    try :
        CAClient.put(medipix_basePvName+":ARR:EnableCallbacks", 1)
        CAClient.put(medipix_basePvName+":ARR:MinCallbackTime", 0)
        
        cam_port = CAClient.get(medipix_basePvName+":CAM:PortName_RBV")
        CAClient.put(medipix_basePvName+":ARR:NDArrayPort", cam_port)

    except (Exception, java.lang.Throwable) as err:
        print "Problem setting callbacks and array port for medipix :ARR plugin", err

def setUseMedipixRoiFromGui(tf, detectorObject=medipix):
    plugins_plotserver_roi = getMedipixPlotserverRoiPlugins(detectorObject)
    plugins_mutable_roi = getMedipixMutableRoiPlugins(detectorObject)

    if tf :
        print "Using Medipix ROI from GUI"
        detectorObject.setAdditionalPluginList(plugins_plotserver_roi)
    else :
        print "Using Medipix ROI from Jython"
        detectorObject.setAdditionalPluginList(plugins_mutable_roi)

def setMedipixRoi(xstart, ystart, xsize, ysize, detectorObject=medipix) :
    print "Setting medipix Jython ROI"
    medipix_roi = getMedipixMutableRoi(detectorObject)

    medipix_roi.setXstart(xstart)
    medipix_roi.setYstart(ystart)
    medipix_roi.setXsize(xsize)
    medipix_roi.setYsize(ysize)
    showMedipixRoi()

def showMedipixRoi(detectorObject=medipix) :
    medipix_roi = getMedipixMutableRoi(detectorObject.getName())
    print "Medipix Jython ROI : start = (%d, %d), size = (%d, %d)"%(medipix_roi.getXstart(), medipix_roi.getYstart(),  medipix_roi.getXsize(), medipix_roi.getYsize())


setupMedipixPlugins(medipix)
setupMedipixPlugins(medipix2)

medipix_roi = getMedipixMutableRoi(medipix)
medipix2_roi = getMedipixMutableRoi(medipix2)

print "Set Medipix to use ROI from GUI : 'setUseMedipixRoiFromGui(True)'. Set to False to use ROI from Jython"
print "Set Medipix Jython ROI : 'setMedipixRoi(xstart, xsize, ystart, ysize)'"
print "Show Medipix Jython ROI : showMedipixRoi()"
