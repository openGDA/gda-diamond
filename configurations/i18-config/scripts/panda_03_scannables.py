print("\nRunning script to setup panda scannables")
print("Panda web UI : http://bl18i-mo-panda-03:8008/gui/PANDA/layout")
from gda.device.panda import EpicsPandaController, PandaController, PandaDetector, BufferedPandaDetector
from gda.device.panda.EpicsPandaController import DataSourceType
from gda.device.panda.PandaController import TriggerType, SequenceTableTimeUnits
from gda.device.panda import SpelCalculator, PVAccess

data_transformer = SpelCalculator()
data_transformer.addOutputExpression("I0", "#A")
data_transformer.addOutputExpression("It", "#B")
data_transformer.addOutputExpression("lnI0It", "#log(#A/#B)")
data_transformer.addOutputExpression("frame_time", "#D - #C")

base_pv="BL18I-TS-PANDA-03:"

data_names=['COUNTER1.OUT.Diff','COUNTER2.OUT.Diff', "PCAP.TS_START.Value", "PCAP.TS_END.Value"]

panda_controller = EpicsPandaController()
panda_controller.setBasePvName(base_pv)
panda_controller.setDataNames(data_names)

panda_controller.setSocketIpAddress("bl18i-mo-panda-03")
panda_controller.setDataSource(DataSourceType.DataSocket)
# panda_controller.setDataSource(DataSourceType.HdfFile) # NB need to also set UseHdfWriter to True on PandaDetector if reading from Hdf file!

panda_controller.configure()
panda_controller.putPvValue("PULSE1:WIDTH:UNITS", 1)
panda_controller.putPvValue("PULSE1:WIDTH", 1e-4)

panda_scalers = PandaDetector()
panda_scalers.setName("panda_scalers")
panda_scalers.setInputNames([])
panda_scalers.setHdfFilenameTemplate("nexus/%d_panda_scalars.hdf")
panda_scalers.setController(panda_controller)
panda_scalers.setUseHdfWriter(True) 
panda_scalers.setReadPandaData(True)
panda_scalers.setUsePulseBlockTrigger(True)

panda_scalers.setTriggerSwitchTimeSecs(0.15)
panda_scalers.setTablePrescaleUnits(SequenceTableTimeUnits.MILLISEC)
panda_scalers.setDataTransformer(data_transformer)

panda_scalers.configure()

buffered_panda_scalers = BufferedPandaDetector()
buffered_panda_scalers.setName("buffered_panda_scalers")
buffered_panda_scalers.setPandaDetector(panda_scalers)
buffered_panda_scalers.setMaximumReadFrames(500)

# set the sequence table row template 
table_row_template = PandaController.SequenceTableRow()
table_row_template.setOutputs1([1,0,0,0,0,0])
table_row_template.setOutputs2([0,0,0,0,0,0])
table_row_template.setTriggerType(TriggerType.BITA_1.getValue());
table_row_template.setTime2(10) #time2 in table units (e.g. ms, usec).  time1 + time2  must be < panda_acalers#triggerSwitchTime

panda_scalers.setTableRowTemplate(table_row_template)



class I18BufferedPandaDetector(BufferedPandaDetector) :
    
    def __init__(self):
        self.counter_pv_name="COUNTER3"
        self.seq_table_out_name = "SEQ1.OUTA"
        self.srgate_out_name = "SRGATE1.OUT"
        self.dead_time_us = 1.0

    # Create PV that returns number of triggers sent from Zebra to PCAP
    def setup_counter_pv(self):
        self.counter = PVAccess(self.panda_controller.getBasePvName()+self.counter_pv_name+":OUT")
    
    def setPandaDetector(self, panda_detector) :
        super(I18BufferedPandaDetector, self).setPandaDetector(panda_detector)
        self.panda_detector = panda_detector
        self.panda_controller = panda_detector.getController()
        
    def setup_design(self) :            
        print("Running 'setup_design'")
        # make sure SRGATE is reset before attaching it to PCAP (so output is 'low')
        # - otherwise 1st frame start during scan setup!
        self.panda_controller.putPvValue("SRGATE1:ENABLE", "ZERO")
        sleep(0.5)
        self.panda_controller.putPvValue("SRGATE1:ENABLE", "ONE")

        # wire up PCap to output of SRGate1 (veto signal from Zebra position triggers)
        self.setup_trigger_source("SRGATE1.OUT")
        
        # setup veto trigger options 
        # PULSE2 produces pulse on rising edge of position trigger. 
        # Width of trigger is used to define the 'dead time' in the veto signal
        self.panda_controller.putPvValue("PULSE2:ENABLE", "ONE")
        self.panda_controller.putPvValue("PULSE2:DELAY", 0.0)
        self.panda_controller.putPvValue("PULSE2:WIDTH:UNITS", 3) #set to us
        self.panda_controller.putPvValue("PULSE2:WIDTH", self.dead_time_us) #set deadtime between veto (detector) triggers
        self.panda_controller.putPvValue("PULSE2:PULSES", 1.0) #1 pulse per input trigger (nneds to be a float for some reason!)

        # SRGATE1 produces veto signal from PULSE2 output (i.e. high between rising edges of trigger)
        self.panda_controller.putPvValue("SRGATE1:SET", "PULSE2.OUT")
        self.panda_controller.putPvValue("SRGATE1:RST", "PULSE2.OUT")
        self.panda_controller.putPvValue("SRGATE1:SET_EDGE", 1) # set on falling edge
        self.panda_controller.putPvValue("SRGATE1:RST_EDGE", 0) # reset on rising edge
 
    def reset_design(self) :            
        # set the PCAP gate and trigger to use sequence table output (SEQ1.OUTA)
        print("Running 'reset_design'")
        self.setup_trigger_source("SEQ1.OUTA")
        
    def setup_trigger_source(self, source_name):
        # attach trigger source to PCAP gate and trigger
        self.panda_controller.putPvValue("PCAP:ENABLE", "ONE") 
        self.panda_controller.putPvValue("PCAP:GATE", source_name)
        self.panda_controller.putPvValue("PCAP:TRIG", source_name)
        
        # attach trigger source to LUT - to trigger TTL out ports on each pulse
        self.panda_controller.putPvValue("LUT1:INPA", source_name)

    def prepare_counter(self):
        # Prepare counter to measure the number of PCap triggers
        # (corresponding to frame index of last frame available to readout)
        self.panda_controller.putPvValue(self.counter_pv_name+":ENABLE", "ZERO")
        self.panda_controller.putPvValue(self.counter_pv_name+":START", -1)
        self.panda_controller.putPvValue(self.counter_pv_name+":STEP", 1.0)
        self.panda_controller.putPvValue(self.counter_pv_name+":ENABLE", "ONE")

    #override 
    # Return the number of triggers sent to PCAP block
    def getNumberFrames(self):
        return int(self.counter.getValue())

    def setContinuousMode(self, on) :
        # this should get called even if exception is thrown during scan or it's stopped early.
        if on :
            self.prepare_counter()
            self.setup_design()
            #self.panda_controller.setPCapArm(0)
        else :
            self.reset_design()
        super(I18BufferedPandaDetector, self).setContinuousMode(on)

qexafs_panda = I18BufferedPandaDetector()
qexafs_panda.setName("qexafs_panda")
qexafs_panda.setPandaDetector(panda_scalers)
qexafs_panda.setMaximumReadFrames(500)
qexafs_panda.setup_counter_pv()

#FFI0 detector using xspress3Odin and panda
i0_data_index = 0
from gda.device.detector import TfgFFoverI0
FFI0_xspress3Odin_panda = TfgFFoverI0()
FFI0_xspress3Odin_panda.setName("FFI0_xspress3Odin_panda")
FFI0_xspress3Odin_panda.setXspress(xspress3Odin)
FFI0_xspress3Odin_panda.setCounterTimer(panda_scalers)
FFI0_xspress3Odin_panda.setI0_channel(i0_data_index)
FFI0_xspress3Odin_panda.configure()

#Qexafs FFI0 detector using xspress3Odin and panda
from uk.ac.gda.devices.detector.xspress3 import Xspress3FFoverI0BufferedDetector
qexafs_FFI0_xspress3Odin_panda = Xspress3FFoverI0BufferedDetector()
qexafs_FFI0_xspress3Odin_panda.setName("qexafs_FFI0_xspress3Odin_panda")
qexafs_FFI0_xspress3Odin_panda.setQexafsScaler(qexafs_panda)
qexafs_FFI0_xspress3Odin_panda.setQexafsXspress(qexafs_xspress3Odin)
qexafs_FFI0_xspress3Odin_panda.setI0_channel(i0_data_index)
qexafs_FFI0_xspress3Odin_panda.configure()

# FFI0 detector using xspress3Mini and panda (xspress3Mini is optional, as part of spring profile)
if "xspress3Mini" in globals():
    FFI0_xspress3Mini_panda = TfgFFoverI0()
    FFI0_xspress3Mini_panda.setName("FFI0_xspress3Mini_panda")
    FFI0_xspress3Mini_panda.setXspress(xspress3Mini)
    FFI0_xspress3Mini_panda.setCounterTimer(panda_scalers)
    FFI0_xspress3Mini_panda.setI0_channel(i0_data_index)
    FFI0_xspress3Mini_panda.configure()

# Example qexafs scan using ContinuousScan :
# cvscan qexafs_energy 3900 4000 1000 20 qexafs_panda

def run_continuous_panda_scan(total_time=10, time_per_point=0.1, external_triggers=False) :
    panda_det = qexafs_panda if external_triggers else buffered_panda_scalers
    num_points = int(total_time/time_per_point)
    print("Running continuous Panda scan using %s\nTotal time : %.3e\nTime per point : %.3e"%(panda_det.getName(), total_time, time_per_point))
    sc=ContinuousScan(cont_scannable, 0, num_points, num_points, total_time, [panda_det])
    sc.runScan()

def run_qexafs_panda_scan(start_energy, end_energy, num_points, total_time=10) :
    print("Running qexafs Panda scan using %s\nE = %.2f ... %.2feV, \nTotal time : %.3e\nNum points: %d" 
          % (qexafs_panda.getName(), start_energy, end_energy, total_time, num_points))
    
    sc=ContinuousScan(qexafs_energy, start_energy, end_energy, num_points, total_time, [qexafs_panda]) #panda])
    sc.getAllScannables().add(sc_dcm_perp)
    sc.getAllScannables().add(sc_dcm_bragg)
    sc.getAllScannables().add(sc_energy_motor)

    sc.runScan()
    
def run_qexafs_tfg_scan(start_energy, end_energy, num_points, total_time=10) :
    print("Running qexafs Tfg scan using %s\nE = %.2f ... %.2feV, \nTotal time : %.3e\nNum points: %d" 
          % (qexafs_counterTimer01.getName(), start_energy, end_energy, total_time, num_points))
    
    sc=ContinuousScan(qexafs_energy, start_energy, end_energy, num_points, total_time, [qexafs_counterTimer01]) #panda])
    sc.runScan()
