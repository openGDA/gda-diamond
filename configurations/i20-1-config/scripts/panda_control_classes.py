from org.slf4j import LoggerFactory

from org.epics.pvaClient import PvaClient
from org.epics.pvdata.pv import *
from gda.device.detector import DetectorBase
from gda.data.swmr import SwmrFileReader
import copy

class PVAccess :
    def __init__(self, pv_name, create_monitor=False):
        self.logger = LoggerFactory.getLogger("PVAccess")
        self.pv_name = pv_name
        self.pva = PvaClient.get("pva")
        self.pv_put = None
        self.pv_get = None
        self.monitor = None
        self.connect()
    
    # Create the channels and connect to them
    def connect(self) :
        self.logger.info("Create PVAccess set and get PVs for {}".format(self.pv_name))
        pv_channel = self.pva.channel(self.pv_name, "pva", 2.0)
        self.pv_put = pv_channel.createPut()
        self.pv_get = pv_channel.createGet()

        for pv in self.pv_put, self.pv_get :
            pv.connect()
            pv.waitConnect()
        
        # Create monitor after connecting the put, get pvs (is this order necessary?)
        if self.create_monitor :
            self.monitor = pv_channel.createMonitor();
            
        self.logger.info("Finished creating PVs")
    
    def create_monitor(self):
        pv_channel = self.pva.channel(self.pv_name, "pva", 2.0)
        monitor = pv_channel.monitor("record[queueSize=1]field()") # PV request - empty field gets the whole structure (EpicsV4DynamicDatasetConnector#MONITOR_REQUEST)
        print("Monitor {}".format(monitor))
        # Throw away an event so monitor behaves as expected in calling code!

        #waitEvent returns True immediately - even with constant PV value!
        monitor.waitEvent(1) # timeout in seconds
        
        # release it
        monitor.releaseEvent()
        
        #next call to waitEvent will block until value actually changes!
        return monitor
    
    def wait_for_value(self, test_function, timeout=10):
        already_good = test_function(self.get_value()) 
        if already_good :
            return True
        
        monitor = self.create_monitor()
        received_callback = monitor.waitEvent(timeout)
        if not received_callback :
            self.logger.warn("Did not receive callback from {} within {} seconds", self.pv_name, timeout)
            
        monitor.stop()
        monitor.destroy()
        return test_function(self.get_value())
    
    def disconnect(self) :
        self.pv_put.destroy()
        self.pv_get.destroy()
        
    def get_data(self) :
        # Update internal value with latest from Epics
        self.pv_get.issueGet()
        self.pv_get.waitGet()
        return self.pv_get.getData()
    
    def get_value(self):
        self.logger.debug("Reading value from {}", self.pv_name)
        get_data = self.get_data()
        enum_pv = self.get_enum_pv(get_data) 
        if enum_pv is not None :
            val = enum_pv.get()
        else :
            val = get_data.getValue().get()
        self.logger.debug("Value = {}",val)
        return val
    
    def get_enum_pv(self, pv_data) :
        value_field = pv_data.getPVStructure().getSubField("value")
        if value_field.getField().getID() == 'enum_t' :
            fields = value_field.getPVFields()
            return fields[0]
        return None

    def put_value(self, value) :
        self.logger.debug("Setting value {} = {}", self.pv_name, value)
        put_data = self.pv_put.getData()
        enum_pv = self.get_enum_pv(put_data) 
        if enum_pv is not None :
            enum_pv.put(value)
        else : 
            if isinstance(value, str) :
                put_data.putString(value)
            if isinstance(value, float) :
                put_data.putDouble(value)
        
        self.pv_put.put()
        
    def put_wait(self, value, **kwargs):
        self.put_value(value)
        PVAccess.wait_for_condition(self, lambda v : v == value, **kwargs)

    def get_structure(self, pv):
        dat=pv.getData()
        return dat.getPVStructure()

    @staticmethod
    def wait_for_condition(pv_access, test_function, timeout=5.0, interval=0.1) :
        time_left = timeout
        while time_left>0 :
            current_value = pv_access.get_value()
            if test_function(current_value) :
                return True
            time_left -= interval
            sleep(interval)
            
        return False

# String values to be used for trigger field
class TriggerValues:
    IMMEDIATE = "Immediate"
    BITA1 = "BITA=1"
    BITA0 = "BITA=0"
    BITB1 = "BITB=1"
    BITB0 = "BITB=0"
    BITC1 = "BITC=1"
    BITC0 = "BITC=0"

class SeqTableTimeUnits:
    MINUTES = 0
    SECONDS = 1
    MILLISEC = 2
    MICROSEC = 3
    
class SeqTableRow:
    def __init__(self):
        self.repeats = 1

        # trigger values need to match available values on Panda - otherwise PvaClient gets 'stuck' and values can't be sent to the table!
        # (that took a morning to figure out :-))
        self.trigger = TriggerValues.IMMEDIATE
        
        self.position = 0
        
        self.time1 = 1
        self.outa1 = 1
        self.outb1 = 0
        self.outc1 = 0
        self.outd1 = 0
        self.oute1 = 0
        self.outf1 = 0
        
        self.time2 = 1
        self.outa2 = 0
        self.outb2 = 0
        self.outc2 = 0
        self.outd2 = 0
        self.oute2 = 0
        self.outf2 = 0

    @staticmethod
    def get_field_type(field_name):
        field_types = {"time1" : PVUIntArray, "time2":PVUIntArray, "repeats" : PVUShortArray,
                                "trigger" : PVStringArray, "position" : PVIntArray}
        if field_name in field_types :
            return field_types[field_name]
        return PVUByteArray



# setup rows in sequence table : values in each SeqTableRow list are set on the rows of the table
def setup_sequence_table_rows(seq_table, seq_table_row_list):
    pv_struct = seq_table.get_structure(seq_table.pv_put)
    table_field = pv_struct.getSubField("value")
    
    var_names = vars(seq_table_row_list[0]) # all variable names in SeqTableRow
    for field_name in var_names :
        # extract field value from each SeqTableRow in list
        all_values = [ vars(row)[field_name] for row in seq_table_row_list]
        
        # lookup the type of the field (PVUIntArray, PVUShortArray etc)
        pv_type= SeqTableRow.get_field_type(field_name)
        
        # set the new value on the field
        print("field_name = {}, values = {}, type = {}".format(field_name, all_values, pv_type))
        field_pv=table_field.getSubField(pv_type, field_name)
        field_pv.setCapacity(len(all_values)) # set the capacity to match the number of values (otherwise might have old values at end of list on the PV record!)
        field_pv.put(0, len(all_values), all_values, 0)
    
    # send updated values to epics
    seq_table.pv_put.put()


def setup_row(seq_table, num_repeats, time1, time2):
    pv_struct = seq_table.get_structure(seq_table.pv_put)
    table_field = pv_struct.getSubField("value")
    
    repeats_field=table_field.getSubField(PVUShortArray, "repeats")
    repeats_field.put(0, 1, [num_repeats], 0)
    
    time1_field = table_field.getSubField(PVUIntArray, "time1")
    time1_field.put(0, 1, [int(time1)], 0)

    time2_field = table_field.getSubField(PVUIntArray, "time2")
    time2_field.put(0, 1, [int(time2)], 0)

    seq_table.pv_put.put()

def grouped_list(value_list) :
    """
        Transform list of values of into list of [value, number of repeats] for each value in list.
        e.g. [1,1,2,2,2,3,4,4,1,1,1] 
            is converted to
        [ [1,2], [2,3], [3,1], [4,2], [1,3] ]
    """
    def last_match_index(value, start_index=0) : 
        for i in range(start_index, len(value_list)) :
            if value_list[i] != value :
                return i-1
        return len(value_list)-1

    grouped_values = []
    start_ind = 0
    total_items = len(value_list)
    while start_ind < total_items :
        v = value_list[start_ind]
        last_ind = last_match_index(v, start_ind)    
        total = last_ind-start_ind + 1
        print("value = {}, start = {}, last = {}, total={}".format(v, start_ind, last_ind, total))
        grouped_values.append( [v, total] )

        start_ind=last_ind+1
        
    return grouped_values


class PandaHdfReader :
    def __init__(self):
        self.logger = LoggerFactory.getLogger("PandaHdfReader")
        self.swmr_file = None
        self.setup_dataset_names(["COUNTER1.OUT.Diff", 'FMC_IN.VAL1.Mean'])
        self.output_format = ["%.4f"]*len(self.dataset_names)
        self.filename = None
        
    def setup_dataset_names(self, dataset_names) :
        self.dataset_names = dataset_names
        self.output_format = ["%.4f"]*len(self.dataset_names)
        
    def connect(self):
        print("Filename : {}".format(self.filename))
        if self.filename is None :
            return
        print("Connecting to swmr file")
        self.swmr_file = SwmrFileReader()
        self.swmr_file.openFile(self.filename)
        for name in self.dataset_names :
            self.swmr_file.addDatasetToRead(name, name)

    def close(self):
        if self.swmr_file is not None and self.swmr_file.isFileOpen() :
            self.swmr_file.releaseFile()

    def get_num_frames(self) :
        return self.swmr_file.getNumAvailableFrames()
    
    def read_data(self, frame_number=-1):
        self.logger.debug("Reading frame {} from hdf file", frame_number)
        num_frames = self.swmr_file.getNumAvailableFrames()
        self.logger.debug("{} frame available to read", num_frames)
        all_data = []
        for name in self.dataset_names :
            self.logger.debug("Reading {}",name)
            if frame_number == -1 :
                dat = self.swmr_file.readDataset(name, [0], [num_frames], [1]).data
            else :
                # single frame
                dat = self.swmr_file.readDataset(name, [frame_number], [1], [1]).data[0]
            all_data.append(dat)
        return all_data
    
class PandaDetector(DetectorBase):
    def __init__(self, name, base_pv):
        self.logger = LoggerFactory.getLogger("PandaDetector")
        self.setInputNames([])
        self.setName(name)
        self.base_pv = base_pv
        self.all_pvs = []
        self.scan_shape = []
        self.trigger_switch_time_sec = 0.25
        self.time_units = SeqTableTimeUnits.MILLISEC
        self.use_hdf_writer = True
        self.hdf_file_template="seq_test.hdf"
        self.hdf_file_subdir = ""
        self.file_flush_period_sec = 0.2
        self.panda_hdf_reader = PandaHdfReader()
        self.read_swmr_file = True
        self.seq_table_row_template = SeqTableRow()
        self.times = []
        
    def connect_pvs(self):
        self.logger.info("Creating PVs")
        self.capture_arm = PVAccess(self.base_pv+"PCAP:ARM")
        self.capture_active = PVAccess(self.base_pv+"PCAP:ACTIVE")

        self.seq_bit_a = PVAccess(self.base_pv+"SEQ1:BITA")
        self.seq_enable = PVAccess(self.base_pv+"SEQ1:ENABLE")
        self.seq_table = PVAccess(self.base_pv+"SEQ1:TABLE")
        self.seq_table_line_repeat = PVAccess(self.base_pv+"SEQ1:LINE_REPEAT")
        self.seq_table_line = PVAccess(self.base_pv+"SEQ1:TABLE_LINE")
        self.seq_state = PVAccess(self.base_pv+"SEQ1:STATE")
        self.seq_active = PVAccess(self.base_pv+"SEQ1:ACTIVE") #get enum value
        self.seq_prescale_units = PVAccess(self.base_pv+"SEQ1:PRESCALE:UNITS")
        self.seq_prescale = PVAccess(self.base_pv+"SEQ1:PRESCALE")

        self.all_pvs = [self.capture_arm, self.seq_bit_a, self.seq_enable, self.seq_table, self.seq_table_line_repeat, self.seq_table_line,
                        self.seq_state, self.seq_active, self.seq_prescale_units, self.seq_prescale]
    
        self.logger.info("Creating Hdf writer PVs")
        self.hdf_directory = PVAccess(self.base_pv+"DATA:HDF_DIRECTORY")
        self.hdf_file_name = PVAccess(self.base_pv+"DATA:HDF_FILE_NAME")
        self.hdf_file_full_path = PVAccess(self.base_pv+"DATA:HDF_FULL_FILE_PATH")
        self.hdf_flush_period = PVAccess(self.base_pv+"DATA:FLUSH_PERIOD")
        self.hdf_capture = PVAccess(self.base_pv+"DATA:CAPTURE") # "0" or "1"
        self.hdf_num_captured = PVAccess(self.base_pv+"DATA:NUM_CAPTURED")
        
        self.all_pvs.extend([self.hdf_directory, self.hdf_file_name, self.hdf_flush_period, self.hdf_capture, self.hdf_num_captured])

    def disconnect_pvs(self):
        self.logger.info("Disconnecting PVs")
        for pv in self.all_pvs :
            pv.disconnect()
    
    def atScanStart(self):
        self.logger.info("atScanStart")

        scan_info = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
        if scan_info is None :
            self.scan_shape = [1]
        else :
            self.scan_shape = [scan_info.getNumberOfPoints()]
        
        self.logger.info("Stopping capture")
        self.seq_bit_a.put_value("ZERO")
        self.capture_arm.put_wait(0)
        
        if self.use_hdf_writer :
            scan_number = scan_info.getScanNumber()
            file_name = self.hdf_file_template.format(scan_number)
            
            pc=InterfaceProvider.getPathConstructor()
            dir_path = pc.getDefaultDataDir() #default data directory
            self.logger.info("Setting up hdf writer : directory = {}, name = {}".format(dir_path, file_name))
            self.hdf_capture.put_value(0)
            self.setup_hdf_writer(dir_path, file_name)

        # Use millisecond time units
        self.seq_prescale_units.put_value(self.time_units)
        self.seq_prescale.put_value(1.0)
        #set the number of points and collection time in the table
        self.logger.info("Setting up sequence table : {} frames, {} sec frame length".format(self.scan_shape[0], self.getCollectionTime()))
        # setup_row(self.seq_table, self.scan_shape[0], self.getCollectionTime()*1000, 0.1*1000)

        # copy setting from the seq_table_row_template set the collection time and number of repeats
        if self.times is not None and len(self.times) > 0:
            times_reps = grouped_list(self.times)
        else :
            times_reps = [[self.getCollectionTime(), self.scan_shape[0]]]
        rows = []
        self.logger.info("Setting up sequence table using time array : {}".format(times_reps))
        for t in times_reps :
            table_row = copy.copy(self.seq_table_row_template)
            table_row.time1 = int(t[0]*1000)
            table_row.repeats = int(t[1])
            self.logger.info("time = {}, repeats = {}".format(table_row.time1, table_row.repeats))
            rows.append(table_row)
        setup_sequence_table_rows(self.seq_table, rows)
    
        sleep(2)
        
        self.logger.info("Starting Hdf writer")
        self.hdf_capture.put_wait(1)
        self.logger.info("Hdf writer started")

        #start the capture
        self.logger.info("Starting capture")
        self.capture_arm.put_wait(1)
        self.logger.info("Capture started")
        
        self.total_frames_collected = 0

    def atScanEnd(self):
        
        # wait for hdf writer to flush remaining frames
        if self.use_hdf_writer and self.hdf_capture.get_value() == 1:
            # Stop the hdf writer
            self.logger.info("Waiting for Hdf writer to finish")
            expected_frames = self.scan_shape[0]
            if not PVAccess.wait_for_condition(self.hdf_num_captured, lambda v : v >= expected_frames) :
                self.logger.warn("problem waiting for Hdf writer frames to be flushed : expected {} frames, but received {}".format(expected_frames, self.hdf_num_captured.get_value()))
            
            self.logger.info("Stopping Hdf writer")
            self.hdf_capture.put_value(0)
            
        # close the connection to the Swmr file
        if self.read_swmr_file :
            self.panda_hdf_reader.close()
        
        # Disarm pcap (Panda PV access fails if left for some time with cap armed but capture has stopped?)
        self.logger.debug("Stopping capture")
        self.capture_arm.put_value(0)

    def stop(self):
        self.logger.warn("Scan stopped early")
        self.atScanEnd()
        
    def atCommandFailure(self):
        self.logger.warn("Scan failed")
        self.atScanEnd()
        
    def setup_hdf_writer(self, directory_name, file_name):
        self.hdf_directory.put_value(str(directory_name))
        self.hdf_file_name.put_value(str(file_name))
        self.hdf_flush_period.put_value(float(self.file_flush_period_sec)) #value needs to be a float

    def collectData(self):
        self.line_repeat_before_collect = self.seq_table_line_repeat.get_value()
        self.table_line_before_collect = self.seq_table_line.get_value()

        self.logger.info("Triggering frame. Current line, repeat : {}, {}".format(self.table_line_before_collect, self.line_repeat_before_collect))
        # set trigger to 1 and back to zero (quickly) to allow 1 trigger to be produced
        self.seq_bit_a.put_value("ONE")
        sleep(self.trigger_switch_time_sec)
        self.seq_bit_a.put_value("ZERO")

    def isBusy(self):
        current_state = self.seq_state.get_value()
        self.logger.debug("isBusy : sequence table state = {}".format(current_state))
        if current_state == 'WAIT_ENABLE' or current_state == "WAIT_TRIGGER" :
            return False
        return True

    def getOutputFormat(self):
        if not self.read_swmr_file :
            return ["%5.5g"]
        return self.panda_hdf_reader.output_format
    
    def getExtraNames(self):
        if not self.read_swmr_file :
            return ['frame number']
        return self.panda_hdf_reader.dataset_names
    
    def readout(self):
        self.total_frames_collected += 1
        
        # Read data from swmr file
        if self.read_swmr_file and self.use_hdf_writer :
            # Wait for frame to be flushed to disc
            self.logger.info("Waiting for frame {} to be flushed to Hdf file", self.total_frames_collected)
            if not PVAccess.wait_for_condition(self.hdf_num_captured, lambda v : v >= self.total_frames_collected) :
                self.logger.warn("problem waiting for Hdf writer flush frames : expected {} frames, but received {}".format(self.total_frames_collected, self.hdf_num_captured.get_value()))
            
            # setup hdf file reader if reading 1st frame
            if self.total_frames_collected == 1 :
                filename=str(self.hdf_file_full_path.get_value())
                self.logger.info("Setting up Swmr file reader for {}", filename)
                self.panda_hdf_reader.filename =  filename
                self.panda_hdf_reader.connect()
            
            # read the data    
            hdf_data = self.panda_hdf_reader.read_data(self.total_frames_collected-1)
            return hdf_data
        
        return self.total_frames_collected # i.e. frame we have just collected

    def createsOwnFiles(self): 
        return False


panda_scalers = PandaDetector("panda_scalers", "BL20J-EA-PANDA-02:")
panda_scalers.connect_pvs()
panda_scalers.seq_table_row_template.trigger = TriggerValues.BITA1
panda_scalers.seq_table_row_template.outa1 = 1
panda_scalers.seq_table_row_template.time2 = 100
panda_scalers.hdf_file_template = "panda_scalar_test_jython.hdf"

panda_hdf_reader = panda_scalers.panda_hdf_reader
panda_hdf_reader.setup_dataset_names(['COUNTER1.OUT.Diff', 'FMC_IN.VAL1.Mean', 'PCAP.GATE_DURATION.Value'])

add_reset_hook(panda_scalers.disconnect_pvs)

