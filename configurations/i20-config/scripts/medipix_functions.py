print "Running medipix_functions.py"

from gda.epics import CAClient

defaultDetector=medipix1


def get_medipix_plugins(detector_object, use_roi_plotserver=True, use_hdf_writer=True) :
    plugin_objects = getPluginsFromFindableObjectHolder(detector_object)
    
    all_plugins = []
    if use_roi_plotserver : 
        all_plugins.append(plugin_objects.get("plot_roi_plugin"))
    else : 
        all_plugins.append(plugin_objects.get("mutable_roi_plugin"))
    
    all_plugins.append(plugin_objects.get("ffi0_plugin"))
    
    if use_hdf_writer :
        all_plugins.append(plugin_objects.get("hdf5_plugin"))
    else :
        all_plugins.append(plugin_objects.get("adarray_plugin"))

    return all_plugins

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

# Retrieve the basePv name for a Medipix detector : 
def getMedipixBasePvName(detectorObject):
    return getPluginsFromFindableObjectHolder(detectorObject).get("basePvName")

def getMedipixMutableRoi(detectorObject):
    return Finder.find(detectorObject.getName()+"_roi")

def setupMedipixPvs(detectorObject=defaultDetector) :
    
    # Get the PV name and plotserver roi plugin object
    basePvName = getMedipixBasePvName(detectorObject)
    
    #set array input port and callbacks for ARR plugin (so live stream works correctly)
    try :
        CAClient.put(basePvName+":ARR:EnableCallbacks", 1)
        CAClient.put(basePvName+":ARR:MinCallbackTime", 0)
        
        cam_port = CAClient.get(basePvName+":CAM:PortName_RBV")
        CAClient.put(basePvName+":ARR:NDArrayPort", cam_port)

    except (Exception, java.lang.Throwable) as err:
        print "Problem setting callbacks and array port for medipix :ARR plugin", err

def setupMedipixPlugins(use_roi_from_gui=True, use_hdf_writer=True, detector_object=defaultDetector):
    print("Setting plugin chain on {} :  using ROI from GUI = {}, use HDF writer = {}".format(detector_object.getName(), str(use_roi_from_gui), str(use_hdf_writer)))
    plugin_list = get_medipix_plugins(detector_object, use_roi_plotserver=use_roi_from_gui, use_hdf_writer=use_hdf_writer)
    detector_object.setAdditionalPluginList(plugin_list)
    
    if "detectorPreparer" in globals() :
        print("Setting up mutable ROI plugins for "+detector_object.getName()+" on detectorPreparer")
        mutable_roi_plugin_chain = get_medipix_plugins(detector_object, use_roi_plotserver=False, use_hdf_writer=use_hdf_writer)
        detectorPreparer.setPluginsForMutableRoi(detector_object, mutable_roi_plugin_chain)

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


setupMedipixPvs(medipix1)
setupMedipixPvs(medipix2)

def setup_default_medipix_plugins() :
    setupMedipixPlugins(use_roi_from_gui=True, use_hdf_writer=True, detector_object=medipix1)
    setupMedipixPlugins(use_roi_from_gui=True, use_hdf_writer=True, detector_object=medipix2)

medipix_roi = getMedipixMutableRoi(medipix1)
medipix2_roi = getMedipixMutableRoi(medipix2)

print """Use setupMedipixPlugins to set Medipix plugin chain to be used for data collection.  Parameters : 

    use_roi_from_gui=True -Set to True (default value) to use detector roi from Gui. 
                            Set to False to use ROi specific by setMedipixRoi function
    
    use_hdf_writer=True  If set to True (default value) Epics Hdf writer plugin will an create Hdf file containing the
                        image data. If set to False, GDA will read the image data from the 'Array' plugin and
                        store it directly in the Nexus file)

    detector_object=medipix1. Detector to apply settings to (use medipix1 or medipix2)
"""

print "Set Medipix Jython ROI : 'setMedipixRoi(xstart, xsize, ystart, ysize)'"
print "Show Medipix Jython ROI : showMedipixRoi()"
print "Use medipix1 or medipix2 as the last parameter to choose a particular detector (e.g. showMedipixRoi(medipix2)) "
