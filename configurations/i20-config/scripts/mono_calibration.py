from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.CentreOfMass import CentreOfMass
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import  GaussianPeakAndBackground
from gdascripts.scan import specscans
import math

def calibrate_mono(calibration_energy,offset_range=0.1,offset_step=0.01,diagnostic_scannable=None):
    
    scan_processor = ScanDataProcessor( [MaxPositionAndValue(),MinPositionAndValue(),CentreOfMass(), GaussianPeakAndBackground() ], globals() )
    ascan  = specscans.Ascan([scan_processor])
    
    # move bragg1 to the calibration energy
    if diagnostic_scannable == None:
        diagnostic_scannable = finder.find("d5_current")
    
    bragg1(calibration_energy)
    
    start_energy = - float(offset_range/2.)
    final_energy = float(offset_range/2.)
    intervals = (final_energy-start_energy)/offset_step
    
    print "Running scan over",braggoffset.getName(),"from",start_energy,"to",final_energy,"in steps of",offset_step,"using",diagnostic_scannable.getName()
    result = ascan([braggoffset, start_energy, final_energy, intervals, diagnostic_scannable])
    calculated_peak = result.peak.result.pos
    print "Peak found at",calculated_peak

    # set the calibration values and press the 'set' buttons
    print "Now will move",braggoffset.getName(),"to",calculated_peak,"and set the calibration."
    #braggoffset(calculated_peak)
    #bragg1_cal_energy(calculated_peak)
    #bragg2_cal_energy(calculated_peak)
    #bragg1_cal_set(1)
    #bragg2_cal_set(1)