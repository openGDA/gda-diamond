from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.CentreOfMass import CentreOfMass
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import  GaussianPeakAndBackground
from gdascripts.scan import specscans
import math

def calibrate_mono(calibration_energy,energy_range=50,energy_step=5,diagnostic_scannable=None):
    
    scan_processor = ScanDataProcessor( [MaxPositionAndValue(),MinPositionAndValue(),CentreOfMass(), GaussianPeakAndBackground() ], globals() )
    ascan  = specscans.Ascan([scan_processor])
#    alias('ascan');print ascan.__doc__.split('\n')[3]
    
    # get what we need from the system
    finder = Finder.getInstance()
    bragg1 = finder.find("bragg1")
    bragg_offset = finder.find("bragg_offset")
    bragg1_cal_energy = finder.find("bragg1_cal_energy")
    bragg1_cal_set = finder.find("bragg1_cal_set")
    bragg2_cal_energy = finder.find("bragg2_cal_energy")
    bragg2_cal_set = finder.find("bragg2_cal_set")
    
    # move bragg1 to the calibration energy
    if diagnostic_scannable == None:
        diagnostic_scannable = finder.find("d5_current")
#    myscan = CentroidScan([bragg1,energy_range,energy_step,diagnostic_scannable])
#    myscan.runScan()
#    filename = myscan.getDataWriter().
    start_energy = calibration_energy - float(energy_range/2.)
    final_energy = calibration_energy + float(energy_range/2.)
    result = ascan([bragg1, start_energy, final_energy, energy_step, diagnostic_scannable])
    
    calculated_peak = scan_processor.result.peak
    if Math.abs(calculated_peak - calibration_energy) > energy_range:
        raise DeviceException("Calibration failed!")

    # set the calibration values and press the 'set' buttons
    scan_processor.go("peak")
    bragg1_cal_set(1)
    bragg2_cal_set(1)