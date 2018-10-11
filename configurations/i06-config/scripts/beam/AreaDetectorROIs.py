from types import ListType
from gda.device.detector.nxdetector.roi import ImutableRectangularIntegerROI
from i06shared.commands.dirFileCommands import finder
from gda.device.detector import NXDetector
from gda.device.detector.nxdetector.plugin.areadetector import ADRoiStatsPair
from gda.scan import ScanInformation

def setupROIs(self, rois, roi_provider_name='pco_roi'):
    '''update ROIs list in GDA ROI provider object but not yet send to EPICS
    This must be called when ROI is changed, and before self.prepareROIsForCollection(areadet)
    @param rois: list of rois i.e. [[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size]]
    '''
    if rois is not ListType:
        raise Exception("Input must be a list of ROIs, each provides a list specifies [x_start,y_start,x_size,y_size]")
    i=1
    newRois=[]
    for roi in rois:
        newRoi=ImutableRectangularIntegerROI(roi[0],roi[1],roi[2],roi[3],'Region'+str(i))
        i +=1
        newRois.append(newRoi)
    roi_provider=finder.find(roi_provider_name)
    roi_provider.updateRois(newRois)
    
def clearROIs(self, roi_provider_name='pco_roi'):
    '''remove all ROIs from the ROI provider
    '''
    roi_provider=finder.find(roi_provider_name)
    roi_provider.updateRois([])

def prepareROIsForCollection(self, areadet, numImages):
    '''configure ROIs and STATs plugins in EPICS for data collection with regions of interests
    @param areadet: must be a NXDetector 
    '''
    if not isinstance(areadet, NXDetector):
        raise Exception("'%s' detector is not a NXDetector! " % (areadet.getName()))
    additional_plugin_list = areadet.getAdditionalPluginList()
    roi_stat_pairs=[]
    for each in additional_plugin_list:
        if isinstance(each, ADRoiStatsPair):
            roi_stat_pairs.append(each)
    for each in roi_stat_pairs:
        #update ROIs and enable and configure EPICS rois and stats plugins
        each.prepareForCollection(numImages, ScanInformation.EMPTY)

    
