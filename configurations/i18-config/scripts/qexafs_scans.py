from gda.device.scannable.zebra import ZebraQexafsScannable
from gda.device.scannable import ScannableMotor, ScannableMotionBase
from time import sleep
import math

# Import cvscan to make it easier to run ContinuousScans
from gda.jython.commands.ScannableCommands import cv as cvscan
from pickle import FALSE
vararg_alias("cvscan")

# Class for I18 to allow them to reuse the B18 position based continuous scannable classes :
# - Use dummy implementation for 'energy control' related functions
# - Motor control uses keV energy units -> override rawGetCurrentPosition to return energy in eV
#    and asynchronousMoveTo to convert energy from eV to keV,
# - Override performContinuousMove to recalculate desiredSpeed to motor units (i.e. kev per second,
# not degrees per second)
# 16/1/2024

class QexafsTest(ZebraQexafsScannable):
    
    def toggleEnergyControl(self):
        pass

    def stopStartEnergyControl(self):
        pass
    
    def setEnergySwitchOn(self):
        pass

    # Return current position in eV
    def rawGetPosition(self):
        current_position_kev = super(QexafsTest,self).rawGetPosition()
        # print(current_position_kev)
        return float(current_position_kev)*1000
    
    def asynchronousMoveTo(self, position_ev):
        position_kev = float(position_ev)/1000.0
        print("Moving %s to %.4f keV"%(self.getName(), position_kev))
        super(QexafsTest, self).asynchronousMoveTo(position_kev)
    
    def setMaxSpeed(self, max_speed):
        self.maxSpeed = max_speed
        
    def prepareForContinuousMove(self):
         # need to reset zebra before trying to configure it (seems to not disarm properly due to stuck 'point download')
        zebra = self.getZebraDevice()
        zebra.reset()
        
        #wait for reset to finish!
        sleep(2)
        
        # These are not (currently) set in QexafsZebraScannable
        # (but they are shared between time and position based trigger sources!)
        zebra.setPCPulseWidth(1e-5) # width of each position trigger
        zebra.setPCPulseMax(10000)  # max number of position trigger pulses to capture
        
        super(QexafsTest, self).prepareForContinuousMove()
        
    def performContinuousMove(self):
        # set the motor speed to the required scan speed (kev per second)
        self.desiredSpeed = 1e-3*math.fabs(self.continuousParameters.getEndPosition() - self.continuousParameters.getStartPosition())//self.continuousParameters.getNumberDataPoints()
        super(QexafsTest, self).performContinuousMove()
        
#from gda.util import CrystalParameters
#CrystalParameters.CrystalSpacing.Si_111.getLabel()

zebra = Finder.find("zebra")

# copy encoder4 value to zebra (i.e. Bragg angle of DCM)
zebra.encCopyMotorPosToZebra(4)

qexafs_energy = QexafsTest()
qexafs_energy.setZebraDevice(zebra)
qexafs_energy.setPcEncType(3) # encoder 4

basePv = "BL18I-MO-DCM-01:"
qexafs_energy.setAccelPV(basePv+"ENERGY.ACCL") 
qexafs_energy.setXtalSwitchPV(basePv+"MP:X:SELECT") # Crystal type PV (Si311 or Si111)
qexafs_energy.setBraggMaxSpeedPV(basePv+"ENERGY.VMAX")
qexafs_energy.setBraggCurrentSpeedPV(basePv+"ENERGY.VELO")
qexafs_energy.setEnergySwitchPV("nothing")

# set motor object to control energy motor (BL18I-MO-DCM-01:ENERGY)
qexafs_energy.setMotor(sc_energy_motor.getMotor())
# qexafs_energy.setMaxSpeed(1) # can also set max speed - kev per second - if don't want to use the value from the motor record

qexafs_energy.setName("qexafs_energy")
qexafs_energy.setOutputFormat(["%7.7g"])  # extra decimal places
qexafs_energy.configure()

# call to set flag to indicate epics channels have been configured
qexafs_energy.initializationCompleted()


from gda.device.scannable import DummyScannable
dummy_scannable = DummyScannable()
dummy_scannable.setName("dummy_scannable")
dummy_scannable.configure()

from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
cont_scannable = QexafsTestingScannable()
cont_scannable.setName("cont_scannable")
cont_scannable.setDelegateScannable(dummy_scannable)
cont_scannable.setMaxMotorSpeed(1000)
cont_scannable.configure()

from gda.device import ContinuousParameters
from gda.scan import ContinuousScan

def generate_continuous_params(start, stop, num_points, total_time) :
    params = ContinuousParameters()
    params.setStartPosition(start)
    params.setEndPosition(stop)
    params.setNumberDataPoints(num_points)
    params.setTotalTime(total_time)
    params.setContinuouslyScannableName(cont_scannable.getName())
    return params

def run_tfg_continuous_scan(num_points, scan_time=5, external_trigger=False, detectors=None) :
    """
        Run a continuous scan using Tfg (qexafs_counterTimer01) and a 'dummy' motor.
        Parameters : 
            num_points - number of frames of data to collect
            scan_time  - how long the scan should take to run (seconds). Optional, default = 5 seconds)
            external_trigger - whether each frame is triggered internally. Optional, default = False.
                               If set to True, Tfg will wait for external trigger before collecting each frame.
                               (Use qexafs_counterTimer01.setTtlSocket(..) to set the Tfg TTL port to use for triggers)
            detector - extra detectors to readout when collecting (Optional). e.g. qexafs_xspress3Odin, qexafs_FFI0_xspress3Odin
    """
    all_detectors = []
    if detectors is not None :
        all_detectors.extend(detectors)
    all_detectors.append(qexafs_counterTimer01)
    
    qexafs_counterTimer01.setUseExternalTriggers(external_trigger)
    sc=ContinuousScan(cont_scannable, 0, num_points, num_points, scan_time, all_detectors)
    sc.runScan()
  


daServer = qexafs_counterTimer01.getScaler().getDaServer()

from gda.data.scan.datawriter import DefaultDataWriterFactory

class TfgScanRunner :
    def __init__(self) :
        self.buffered_scaler = None
        self.frame_dead_time = 0.0
        self.external_trigger_frames = False
        self.external_trigger_start = False
        self.initial_group_command = ""
        self.num_cycles = 1
        self.extra_scannables = None 

        self.nexus_name_template = "" 
        self.ascii_name_template = "" 

    def apply_settings(self) :
        self.buffered_scaler.setExternalTriggeredFrames(self.external_trigger_frames)
        self.buffered_scaler.setExternalTriggerStart(self.external_trigger_start)
        self.buffered_scaler.setFrameDeadTime(self.frame_dead_time)
        self.buffered_scaler.setGroupInitialCommand(self.initial_group_command);   
        self.buffered_scaler.setNumCycles(self.num_cycles)
        if self.num_cycles > 1 :
            self.buffered_scaler.setFrameCountDuringCycles(False)
        else :
            self.buffered_scaler.setFrameCountDuringCycles(True)        
        
    def show_settings(self) :
        print("Settings in tfgScanRunner : ")
        for k, v in self.__dict__.items() :
            val = "\"%s\""%(v) if isinstance(v, str) else v
            print("\t%s = %s"%(k, val))

    def create_datawriter(self) :
        dw=DefaultDataWriterFactory.createDataWriterFromFactory()
        if len(self.nexus_name_template) > 0 :
            dw.setNexusFileNameTemplate(self.nexus_name_template)
        if len(self.ascii_name_template) > 0 :
            dw.setAsciiFileNameTemplate(self.ascii_name_template)
        # set the ascii and file
        return dw
    
    # Add scan parameters as metadata
    def setup_metadata(self, num_points, time_per_point) :
        meta_add("tfg_num_cycles", self.num_cycles)
        meta_add("tfg_time_per_point", time_per_point)
        meta_add("tfg_num_points", num_points)

    # Remove the custom metadata values
    def clear_metadata(self):
        metashop=Finder.find("metashop")
        metashop.remove("tfg_num_cycles")
        metashop.remove("tfg_time_per_point")
        metashop.remove("tfg_num_points")
    
    def show_message(self, message):
        InterfaceProvider.getTerminalPrinter().print(message)
        
    def run_scan(self, num_points, time_per_point) :
        # run the scan
        try :
            sc = self.generate_scan(num_points, time_per_point)
            sc.runScan()
        finally : 
            self.show_message("Clearing Tfg metadata after scan")
            self.clear_metadata()

    def generate_scan(self, num_points, time_per_point):
        
        msg = "Running Tfg scan : %d points, %.5g sec per point, %d cycles"%(num_points, time_per_point, self.num_cycles)
        self.show_message(msg)
        
        # apply class settings to buffered scaler
        self.apply_settings()
        
        # generate scan object
        scan_time = time_per_point*num_points
        # self.buffered_scaler.stop()
        sc=ContinuousScan(cont_scannable, 0, num_points, num_points, scan_time, [self.buffered_scaler])

        if self.extra_scannables is not None and len(self.extra_scannables) > 0 :
            sc.getAllScannables().addAll(self.extra_scannables)

        # setup the metadata
        self.setup_metadata(num_points, time_per_point)

        # inject datawriter        
        datawriter = self.create_datawriter()
        sc.setDataWriter(datawriter)
        
        return sc

   
# Scan runner for laser experiment     
tfgScanRunner= TfgScanRunner()
tfgScanRunner.buffered_scaler = qexafs_counterTimer01

output_directory = ""
filename_template = ""

if len(filename_template) == 0 :
    filename_template = "%d"

tfgScanRunner.ascii_name_template = "%s/ascii/%s.dat"%(output_directory, filename_template)
tfgScanRunner.nexus_name_template = "%s/nexus/%s.nxs"%(output_directory, filename_template)

delay_after_trigger = 50e-9
tfgScanRunner.initial_group_command = "1 %.5g 0 0 0 8 0"%(delay_after_trigger)

print("Adding 'run_tfg_continuous_scan' and 'tfgScanRunner'.\nUse help(run_tfg_continuous_scan), for more info. ")
