from gda.device.detector import BufferedEdeDetector
from gda.factory import Finder
from gda.device.lima.LimaCCD import AcqTriggerMode

from gda.device.scannable import TurboXasScannable
from gda.device.zebra import ZebraGatePulsePreparer
from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
import math

print "running alignment_stage_pos_scan.py"

Finder = Finder.getInstance();
#  as_hoffset = Finder.find("as_hoffset")
# scaler_for_zebra = Finder.find("scaler_for_zebra")
as_hoffset_motor = as_hoffset.getMotor()

zebra_preparer = ZebraGatePulsePreparer()
zebra_preparer.setZebraDevice(zebra_device)
zebra_preparer.setPositionTriggerEncoder(0) # 0 = Zebra.PC_ENC_ENC1 for alignment stage
zebra_preparer.setTtlOutputPort(31) # Same as TurboXas
zebra_preparer.setPositionTriggerTimeUnits(1) # Times in seconds

alignment_stage_txas = TurboXasScannable()
alignment_stage_txas.setName("alignment_stage_txas")
alignment_stage_txas.setMotor(as_hoffset_motor)
alignment_stage_txas.setZebraDevice(zebra_device)
alignment_stage_txas.setZebraGatePulsePreparer(zebra_preparer)
alignment_stage_txas.configure()
alignment_stage_txas.setMaxMotorSpeed(0.8); # max speed from Epics = 1.0mm/sec
alignment_stage_txas.setRampDistance(0.02)

alignment_stage_qexafs = QexafsTestingScannable()
alignment_stage_qexafs.setName("alignment_stage_qexafs")
alignment_stage_qexafs.setMotor(as_hoffset_motor)
alignment_stage_qexafs.setOutputFormat(["%.4f"])
alignment_stage_qexafs.setMaxMotorSpeed(0.8); # max speed from Epics = 1.0mm/sec
alignment_stage_qexafs.setRampDistance(0.02)


"""
No zebra used for synchronization. Motor move and tfg start at same time 
"""
def runScanUnsyncronized(start, stop, readouts, time, detectors ) :
    scaler_for_zebra.setUseInternalTriggeredFrames(True) # use software start for Tfg triggers
    alignment_stage_qexafs.setRampDistance(0.0);
    cs=ContinuousScan(alignment_stage_qexafs, start, stop, readouts, time, detectors)
    cs.getAllScannables().add(as_hoffset) # add hoffset scannable to get the real position at each scan data point
    cs.runScan()

num_accumulations = 1
accumulation_readout_time = 0.5e-3

def prepareFrelon(scan_start, scan_end, scan_num_readouts, time) :
    # scan_num_readouts = math.ceil( float((scan_end - scan_start)/scan_step) )
    time_per_readout = time/scan_num_readouts
    print "Number of readouts : %.5f sec"%(scan_num_readouts)
    print "Time per readout : %.5f sec"%(time_per_readout)  
    
    accumulation_time = time_per_readout/num_accumulations - accumulation_readout_time
    print "Accumulations per readout  : %d"%(num_accumulations)
    print "Time per accumulation : %.5f sec"%(accumulation_time)
        
    buffered_frelon.prepareDetectorForCollection( int(scan_num_readouts), time_per_readout, accumulation_time, int(num_accumulations))
    return scan_num_readouts

def runScanUnsyncronizedFrelon(scan_start, scan_end, scan_num_readouts, time ) :
    prepareFrelon(scan_start, scan_end, scan_num_readouts, time)
    buffered_frelon.setExternalTriggerMode(True) # Software start, not triggered by tfg
    runScanUnsyncronized(float(scan_start), float(scan_end), int(scan_num_readouts), float(time), [scaler_for_zebra, buffered_frelon])
    
    
def runScanSyncronized(start, stop, num_readouts, time, detectors ) :
    cs=ContinuousScan(alignment_stage_txas, start, stop, num_readouts, time, detectors)
    cs.runScan()
    
## Buffered detector to use for continuous scan
def getBufferedFrelon() :
    bd = BufferedEdeDetector()
    bd.setName("buffered_frelon")
    bd.setDetector(Finder.find("frelon"))
    bd.setExternalTriggerMode(True)
    return bd

def runScanSynchronizedFrelon(scan_start, scan_end, scan_step, time):
    num_accumulations = 1
    scan_num_readouts = prepareFrelon(scan_start, scan_end, scan_step, time)

    fr = buffered_frelon.getDetector()
    fr.fetchDetectorSettings()
    detData = fr.getDetectorData();
    #detData.setTriggerMode(AcqTriggerMode.INTERNAL_TRIGGER)
    detData.setTriggerMode(AcqTriggerMode.EXTERNAL_TRIGGER_MULTI)
    runScanSyncronized(scan_start, scan_end, scan_step, [scaler_for_zebra, buffered_frelon])
    

buffered_frelon = getBufferedFrelon()

def delete_scannables() :
    global alignment_stage_txas
    global  alignment_stage_qexafs
    global buffered_frelon
    del alignment_stage_txas
    del alignment_stage_qexafs
    del buffered_frelon