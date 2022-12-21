'''
a routine in GDA that centre the X-ray beam in the PEEM field of view horizontally and vertically using the M4 and M5 fine pitch actuators.

Created on Jun 24, 2022

@author: fy65
'''
from i06shared.commands.beamline import lastscan
from gdascripts.scan.process.ScanDataProcessorResult import getDatasetFromLoadedFile
from gdaserver import medipix # @UnresolvedImport
from beam.roi_scannable import RoiStatScannable
from peem.leem_scannables import leem_FOV_A
from i06shared.scan.installStandardScansWithAdditionalScanListeners import cscan
from scannables.m4m5finepitches import m4fpitch, m5fpitch
import scisoftpy as dnp
import logging
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import GaussianPeak

logger = logging.getLogger(__name__)

def find_peak_position(filepath, xfieldname, yfieldname):
    filepath = str(filepath)
    logger.debug('Loading scan file: %s', filepath)
    last_scan_file = dnp.io.load(filepath, formats=('nx','srs'))
    try:
        x_dataset = getDatasetFromLoadedFile(last_scan_file, xfieldname)
        y_dataset = getDatasetFromLoadedFile(last_scan_file, yfieldname)
    except KeyError, e:
        logger.error('Error loading datasets', exc_info=e)
        return "<" + e.message + ">"
    
    # Check the datasets are processable
    if x_dataset.shape[0] in (0,1):
        logger.debug('Scan too short to process (shape=%s)', x_dataset.shape[0])
        return "Scan too short to process sensibly"
    if x_dataset.shape[0] != y_dataset.shape[0]:
        logger.error('Scan dimensions do not match (%s != %s)', x_dataset.shape[0], y_dataset.shape[0])
        return "Scan dimensions mismatch! (length(x)=%d != length(y)=%d)" % (x_dataset.shape[0], y_dataset.shape[0])
    
    if y_dataset.max() - y_dataset.min() == 0:
        raise ValueError("There is no peak")
    x, y = to_dnp_arrays(x_dataset, y_dataset)

    gaussianpeak = GaussianPeak()
    fit_result = gaussianpeak.getFitResult(x,y)
    result = gaussianpeak.getResults(fit_result)
    return result['pos']

def to_dnp_arrays(*args):
    return [dnp.array(arg) for arg in args]

def centerBeam(number_of_steps = 20, exposure_time = 0.1):
    
    # create ROIs in the format of [x_start, y_start, x_size, y_size]
    top_roi = [1, 1, 1000, 250]  # top
    bottom_roi = [1, 750, 1000, 250]  # bottom
    
    right_roi = [750, 1, 250, 1000]  # right
    left_roi = [1, 1, 250, 1000]  # left
    
    
    roitop = RoiStatScannable("roitop", medipix, top_roi, 7, pv_root_name="BL06I-EA-DET-02")
    roitop.configure()
    roibottom = RoiStatScannable("roibottom", medipix, bottom_roi, 8, pv_root_name="BL06I-EA-DET-02")
    roibottom.configure()
    
    roileft = RoiStatScannable("roileft", medipix, left_roi, 9, pv_root_name="BL06I-EA-DET-02")
    roileft.configure()
    roiright = RoiStatScannable("roiright", medipix, right_roi, 10, pv_root_name="BL06I-EA-DET-02")
    roiright.configure()
    
    scan_range = float(leem_FOV_A.getPosition())*10/320
    
    # scan vertically
    cscan(m4fpitch, scan_range/2.0, scan_range*2/number_of_steps, medipix, exposure_time, roitop, roibottom)
    
    roitop_peak = find_peak_position(str(lastscan()), m4fpitch.name, roitop.name)
    roibottom_peak = find_peak_position(str(lastscan()), m4fpitch.name, roibottom.name)    
    vertical_centre = (roitop_peak + roibottom_peak) / 2.0
    print("---> vertical centre = ",vertical_centre)
    #centre beam in vertical direction
    m4fpitch.moveTo(vertical_centre)
    
    #scan horizontally
    cscan(m5fpitch, scan_range/2.0, 20, medipix, 0.1, roileft, roiright)
    
    roileft_peak = find_peak_position(str(lastscan()), m5fpitch.name, roileft.name)
    roiright_peak = find_peak_position(str(lastscan()), m5fpitch.name, roiright.name)
    hortizontal_centre = (roileft_peak + roiright_peak) / 2.0
    #centre beam in vertical direction
    m5fpitch.moveTo(hortizontal_centre)
    
    roitop.deconfigure()
    roibottom.deconfigure()
    roileft.deconfigure()
    roiright.deconfigure()
    
    print("Centre beam is completed")


##############################tests#####################

def centerBeam2(number_of_steps = 50, exposure_time = 0.1):
    
    # create ROIs in the format of [x_start, y_start, x_size, y_size]
    top_roi = [1, 1, 1000, 250]  # top
    bottom_roi = [1, 750, 1000, 250]  # bottom
    
    right_roi = [750, 1, 250, 1000]  # right
    left_roi = [1, 1, 250, 1000]  # left
    
    
    roitop = RoiStatScannable("roitop", medipix, top_roi, 7, pv_root_name="BL06I-EA-DET-02")
    roitop.configure()
    roibottom = RoiStatScannable("roibottom", medipix, bottom_roi, 8, pv_root_name="BL06I-EA-DET-02")
    roibottom.configure()
    
    roileft = RoiStatScannable("roileft", medipix, left_roi, 9, pv_root_name="BL06I-EA-DET-02")
    roileft.configure()
    roiright = RoiStatScannable("roiright", medipix, right_roi, 10, pv_root_name="BL06I-EA-DET-02")
    roiright.configure()
    
    scan_range = float(leem_FOV_A.getPosition())*3/320
    
    # scan vertically
    cscan(m4fpitch, scan_range/2.0, scan_range/number_of_steps, medipix, exposure_time, roitop, roibottom)
    
    roitop_peak = find_peak_position(str(lastscan()), m4fpitch.name, roitop.name)
    roibottom_peak = find_peak_position(str(lastscan()), m4fpitch.name, roibottom.name)    
    vertical_centre = (roitop_peak + roibottom_peak) / 2.0
    print("---> vertical centre = ",vertical_centre)
    
    #centre beam in vertical direction
    #m4fpitch.moveTo(vertical_centre)
    
    roitop.deconfigure()
    roibottom.deconfigure()
    roileft.deconfigure()
    roiright.deconfigure()
    
    print("Centre beam is completed")


