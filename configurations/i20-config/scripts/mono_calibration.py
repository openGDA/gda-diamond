from gdascripts.scan.process.ScanDataProcessor import ScanDataProcessor
from gdascripts.analysis.datasetprocessor.oned.MaxPositionAndValue import MaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.CentreOfMass import CentreOfMass
from gdascripts.analysis.datasetprocessor.oned.GaussianPeakAndBackground import  GaussianPeakAndBackground
from gdascripts.scan import specscans
import math
from BeamlineParameters import JythonNameSpaceMapping

class calibrate_mono:
    
    def __init__(self,offset_range=20.0,offset_step=0.2,acquire_time=1.0):
        '''
            Usage: calibrate_mono mono_peak_energy actual_peak_energy [range of offset scan] [ step isze of offset scan] [acquire time of offset scan]
        '''
        self.offset_range = offset_range
        self.offset_step = offset_step
        self.acquire_time = acquire_time
        self.current_peak_energy = None
        self.expected_energy = None
        
    def sefCurrent(self, current_peak_energy):
        self.current_peak_energy = current_peak_energy
        
    def setExpected(self, expected_energy):
        self.expected_energy = expected_energy
    
    def __call__(self):
        if self.current_peak_energy == None:
            print "Cannot calibrate mono as the current peak energy has not been set!"
            return
        if self.expected_energy == None:
            print "Cannot calibrate mono as the expected peak energy has not been set!"
            return
        print "*****************"
        print "Running mono calibration"
        print "Using current peak energy of ",self.current_peak_energy,"eV"
        print "Using expected peak energy of ",self.expected_energy,"eV"
        scan_processor = ScanDataProcessor( [MaxPositionAndValue(),MinPositionAndValue(),CentreOfMass(), GaussianPeakAndBackground() ], globals() )
        ascan  = specscans.Ascan([scan_processor])
        # move bragg1 to the calibration energy
        jnm = JythonNameSpaceMapping()
        diagnostic_scannable = jnm.d5
        print "Moving d5 screen in to beam and set the gain (this may take a while!)..."
        d5_screen('Diode')
        d5_gain(3)
        print "Moving bragg1 to",current_peak_energy,"eV using current (old) calibration"
        bragg1(current_peak_energy)
        start_energy = - float(offset_range/2.)
        final_energy = float(offset_range/2.)
        intervals = (final_energy-start_energy)/offset_step
        print "Running scan over",braggoffset.getName(),"from",start_energy,"to",final_energy,"in steps of",offset_step,"using",diagnostic_scannable.getName(),"collecting for",acquire_time,"s"
        result = ascan([braggoffset, start_energy, final_energy, intervals, diagnostic_scannable,acquire_time])
        calculated_peak = result.peak.result.pos
        print "Peak found at",calculated_peak
        # set the calibration values and press the 'set' buttons
        print "Now will move",braggoffset.getName(),"to",calculated_peak,"and set the calibration."
        #braggoffset(calculated_peak)
        #bragg1_cal_energy(expected_energy)
        #bragg2_cal_energy(expected_energy)
        #bragg1_cal_set(1)
        #bragg2_cal_set(1)
        print "Moving d5 screen out of beam (this may take a while!)..."
        d5_screen('Empty')
        print "Calibration complete."