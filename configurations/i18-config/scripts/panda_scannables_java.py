print("\nRunning script to setup panda scannables")

from gda.device.panda import EpicsPandaController, PandaController, PandaDetector, DataSocketDetector, BufferedPandaDetector
from gda.device.panda.PandaController import TriggerType, SequenceTableTimeUnits

base_pv="BL18I-TS-PANDA-01:"

panda_control = EpicsPandaController()
panda_control.setBasePvName(base_pv)
panda_control.configure()

panda_scalers = PandaDetector()
panda_scalers.setName("panda_scalers")
panda_scalers.setInputNames([])
# panda_scalers.setHdfFilenameTemplate("panda_scalar_test_%d.hdf")
panda_scalers.setHdfFilenameTemplate("panda_scalars_%d.hdf")
panda_scalers.setController(panda_control)

panda_scalers.setUseHdfWriter(False) #True)
panda_scalers.setReadSwmrFile(False) #True)

panda_scalers.setTriggerSwitchTimeSecs(0.15)
panda_scalers.setTablePrescaleUnits(SequenceTableTimeUnits.MILLISEC)

panda_scalers.configure()

buffered_panda_scalers = BufferedPandaDetector()
buffered_panda_scalers.setName("buffered_panda_scalers")
buffered_panda_scalers.setPandaDetector(panda_scalers)
buffered_panda_scalers.setMaximumReadFrames(500)

hdf_reader = panda_scalers.getPandaHdfReader()

data_names = "PCAP.TS_START.Value", "PCAP.TS_END.Value", "PCAP.TS_TRIG.Value", "COUNTER1.OUT.Diff", "COUNTER2.OUT.Diff", "COUNTER3.OUT.Diff"
hdf_reader.setDataNames(data_names)
hdf_reader.setHdfPollIntervalSec(0.2)
hdf_reader.setHdfPollNumRetries(20)

# set the sequence table row template 
table_row_template = PandaController.SequenceTableRow()
table_row_template.setOutputs1([1,0,0,0,0,0])
table_row_template.setOutputs2([0,0,0,0,0,0])
table_row_template.setTriggerType(TriggerType.BITA_1.getValue());
table_row_template.setTime2(100) #time2 in table units (e.g. ms, usec).  time1 + time2  must be < panda_acalers#triggerSwitchTime

panda_scalers.setTableRowTemplate(table_row_template)

socket_detector = DataSocketDetector()
socket_detector.setSocketIpAddress("bl18i-mo-panda-01") # same url as web gui
socket_detector.configure()
socket_detector.setName("socket_detector")
socket_detector.setDataNames(data_names)
socket_detector.setMaximumReadFrames(500)

class QexafsPanda(BufferedPandaDetector) :
    
    def setPandaDetector(self, panda_detector) :
        super(QexafsPanda, self).setPandaDetector(panda_detector)
        self.panda_detector = panda_detector
        self.panda_controller = panda_detector.getController()
        
    def setup_design(self) :            
        # set the pcap gate and trigger to use TTL1 input (rather than sequence table)
        self.panda_controller.putPvValue("PCAP:ENABLE", "ONE") 
        self.panda_controller.putPvValue("PCAP:GATE", "SRGATE1.OUT") # "TTLIN1.VAL")
        self.panda_controller.putPvValue("PCAP:TRIG", "SRGATE1.OUT") # "TTLIN1.VAL")
        
        # ttl1 input attached to SRGATE (TTL veto from zebra encoder pulses)
        self.panda_controller.putPvValue("TTLOUT1:VAL", "SRGATE1.OUT")
    
    def setContinuousMode(self, on) :
        if on :
            self.panda_controller.setPCapArm(0)
            
            self.setup_design()
            if self.pandaDetector.isUseHdfWriter() :
                self.panda_detector.setupHdfWriter()
                self.panda_controller.setHdfCapture(1)
                
            self.panda_controller.setPCapArm(1)

    def atScanEnd(self):
        if self.panda_detector.isUseHdfWriter() :
            hdf_sleep_sec = 1.0
            print("Waiting for {} seconds at end of scan to stop Hdf writer".format(hdf_sleep_sec))
            sleep(hdf_sleep_sec)
            self.panda_controller.setHdfCapture(0)
        super(QexafsPanda, self).atScanEnd()

qexafs_panda = QexafsPanda()
qexafs_panda.setName("qexafs_panda")
qexafs_panda.setPandaDetector(panda_scalers)
qexafs_panda.setMaximumReadFrames(500)
