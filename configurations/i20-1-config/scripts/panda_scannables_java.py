print("\nRunning script to setup panda scannables")

from gda.device.panda import PVAccess, EpicsPandaController, PandaController, PandaDetector, DataSocketDetector, BufferedPandaDetector
from gda.device.panda.PandaController import TriggerType, SequenceTableTimeUnits

from java.net import Socket
from java.io import BufferedWriter, BufferedReader
from java.io import OutputStreamWriter, InputStreamReader

# Prototype Jython version of Datasocket - to collect franes of data from Panda TCP data socket.
class DataSocket :
    def __init__(self) :
        self.socket = None 
        self.input = None
        self.all_lines = []
        self.data_start_index = -1
        
    def connect(self, ip_address, port):
        self.socket = Socket(ip_address, port)
        self.output = BufferedWriter(OutputStreamWriter(self.socket.getOutputStream())) # send command to socket
        self.input = BufferedReader(InputStreamReader(self.socket.getInputStream())) # read from socket
        self.sendCommand("\n")
        
    def readline(self) :
        return self.input.readLine()
    
    def sendCommand(self, command):
        self.output.write(command)
        self.output.flush()
    
    def clearData(self):
        self.all_lines = []

    def updateData(self):
        while self.input.ready() :
            self.all_lines.append(self.input.readLine())
    
    def getData(self):
        if self.data_start_index > 0 : 
            return self.all_lines[self.data_start_index:]
        
    def parseHeader(self):
        if "fields:" in self.all_lines :
            field_start = self.all_lines.index("fields:")+1
            field_end = self.all_lines.index("", field_start)
            print("Field range : {} {}".format(field_start, field_end))
            field_list = [ line.strip().split(" ")[0] for line in self.all_lines[field_start:field_end]]
            print("Field list : {}".format(field_list))
            self.data_start_index = field_end+1
            
    
data_socket = DataSocket()
data_socket.connect("bl20j-ts-panda-02",8889)

# Java class to wrap jython lambda as Java Function object
from java.util.function import Function 
class JavaFunction(Function) :
    def __init__(self, jython_lambda) :
        self.jython_lambda = jython_lambda
    def apply(self, val):
        return self.jython_lambda(val)

base_pv="BL20J-EA-PANDA-02:"

print("Creating capture and seq PVs")
capture_arm = PVAccess(base_pv+"PCAP:ARM")
capture_active = PVAccess(base_pv+"PCAP:ACTIVE")

seq_bit_a = PVAccess(base_pv+"SEQ1:BITA")
seq_enable = PVAccess(base_pv+"SEQ1:ENABLE")
seq_table = PVAccess(base_pv+"SEQ1:TABLE")
seq_table_line_repeat = PVAccess(base_pv+"SEQ1:LINE_REPEAT")
seq_table_line = PVAccess(base_pv+"SEQ1:TABLE_LINE")
seq_state = PVAccess(base_pv+"SEQ1:STATE")
seq_active = PVAccess(base_pv+"SEQ1:ACTIVE") #get enum value
seq_prescale_units = PVAccess(base_pv+"SEQ1:PRESCALE:UNITS")
seq_prescale = PVAccess(base_pv+"SEQ1:PRESCALE")

all_pvs = [capture_arm, seq_bit_a, seq_enable, seq_table, seq_table_line_repeat, seq_table_line,
                seq_state, seq_active, seq_prescale_units, seq_prescale]

print("Creating Hdf writer PVs")
hdf_directory = PVAccess(base_pv+"DATA:HDF_DIRECTORY")
hdf_file_name = PVAccess(base_pv+"DATA:HDF_FILE_NAME")
hdf_file_full_path = PVAccess(base_pv+"DATA:HDF_FULL_FILE_PATH")
hdf_flush_period = PVAccess(base_pv+"DATA:FLUSH_PERIOD")
hdf_capture = PVAccess(base_pv+"DATA:CAPTURE") # "0" or "1"
hdf_num_captured = PVAccess(base_pv+"DATA:NUM_CAPTURED")

all_pvs.extend([hdf_directory, hdf_file_name, hdf_flush_period, hdf_capture, hdf_num_captured])

def disconnect_pvs(self):
    print("Disconnecting PVs")
    for pv in all_pvs :
        pv.disconnect()

 
add_reset_hook(disconnect_pvs)

panda_control = EpicsPandaController()
panda_control.setBasePvName(base_pv)
panda_control.configure()

panda_scalers = PandaDetector()
panda_scalers.setName("panda_scalers")
panda_scalers.setInputNames([])
# panda_scalers.setHdfFilenameTemplate("panda_scalar_test_%d.hdf")
panda_scalers.setHdfFilenameTemplate("panda_scalars_%d.hdf")
panda_scalers.setController(panda_control)
panda_scalers.setUseHdfWriter(True)
panda_scalers.setReadSwmrFile(True)
panda_scalers.setTriggerSwitchTimeSecs(0.15)
# panda_scalers.setTablePrescaleUnits(SequenceTableTimeUnits.MILLISEC)
panda_scalers.setTablePrescaleUnits(SequenceTableTimeUnits.MICROSEC)

panda_scalers.configure()

buffered_panda_scalers = BufferedPandaDetector()
buffered_panda_scalers.setName("buffered_panda_scalers")
buffered_panda_scalers.setPandaScalers(panda_scalers)
buffered_panda_scalers.setMaximumReadFrames(500)

hdf_reader = panda_scalers.getPandaHdfReader()

data_names=['COUNTER1.OUT.Diff', 'FMC_IN.VAL1.Mean', 'FMC_IN.VAL1.Max', 'FMC_IN.VAL1.Min', 'PCAP.GATE_DURATION.Value']
hdf_reader.setDataNames(data_names)
# hdf_reader.setDataNames(['PCAP.GATE_DURATION.Value'])
hdf_reader.setHdfPollIntervalSec(0.2)
hdf_reader.setHdfPollNumRetries(20)

# ADC position settings
# BL20J-EA-PANDA-02:POSITIONS:12:NAME #FMC_IN:VAL1
# CAPTURE "Min Max Mean"
# SCALE : 4.65661287e-9

# set the sequence table row template 
table_row_template = PandaController.SequenceTableRow()
table_row_template.setOutputs1([1,0,0,0,0,0])
table_row_template.setOutputs2([0,0,0,0,0,0])
table_row_template.setTriggerType(TriggerType.BITA_1.getValue());
table_row_template.setTime2(100) #time2 in table units (e.g. ms, usec).  time1 + time2  must be < panda_acalers#triggerSwitchTime

panda_scalers.setTableRowTemplate(table_row_template)


#pos_trigger="POSA>=POSITION"
#table_row_template.setTriggerType(pos_trigger)
#scale_factor=4.65661287e-9 # volts to counts conversion factor for ADC1
#table_row_template.setPosition(int(3.9786/scale_factor))
table_row_template.setTime2(0)

socket_detector = DataSocketDetector()
socket_detector.setName("socket_detector")
socket_detector.setDataNames(["PCAP.GATE_DURATION", "COUNTER1.OUT", "PCAP.TS_TRIG", "FMC_IN.VAL1"])
socket_detector.setMaximumReadFrames(500)

