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

# Find the the 2 'additional plugin' lists : one to  use ROI from plotserver and one to use mutable ROI
def setupMedipixPlugins() :
    global plugins_plotserver_roi
    global plugins_mutable_roi
    global medipix_roi
    global medipix_basePvName

    #  Get the findable map containing the additional plugin lists
    medipix_plugins = Finder.getInstance().find("medipix_plugins")

    # Get the two plugin lists
    plugins_plotserver_roi = medipix_plugins.get("plugins_plotserver_roi")
    plugins_mutable_roi = medipix_plugins.get("plugins_mutable_roi")
    medipix_basePvName = medipix_plugins.get("medipix_basePvName")

    # get the mutable roi used by plugins_mutable_roi
    medipix_roi = Finder.getInstance().find("medipix_roi")

    # Set the initial plugin list on the detector
    medipix.setAdditionalPluginList(plugins_plotserver_roi)

def setUseMedipixRoiFromGui(tf):
    global plugins_plotserver_roi
    global plugins_mutable_roi
    if tf :
        print "Using Medipix ROI from GUI"
        medipix.setAdditionalPluginList(plugins_plotserver_roi)
    else :
        print "Using Medipix ROI from Jython"
        medipix.setAdditionalPluginList(plugins_mutable_roi)

def setMedipixRoi(xstart, ystart, xsize, ysize) :
    print "Setting medipix Jython ROI"
    global medipix_roi
    medipix_roi.setXstart(xstart)
    medipix_roi.setYstart(ystart)
    medipix_roi.setXsize(xsize)
    medipix_roi.setYsize(ysize)
    showMedipixRoi()

def showMedipixRoi() :
    global medipix_roi
    print "Medipix Jython ROI : start = (%d, %d), size = (%d, %d)"%(medipix_roi.getXstart(), medipix_roi.getYstart(),  medipix_roi.getXsize(), medipix_roi.getYsize())

setupMedipixPlugins()
print "Set Medipix to use ROI from GUI : 'setUseMedipixRoiFromGui(True)'. Set to False to use ROI from Jython"
print "Set Medipix Jython ROI : 'setMedipixRoi(xstart, xsize, ystart, ysize)'"
print "Show Medipix Jython ROI : showMedipixRoi()"

