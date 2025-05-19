import uk.ac.diamond.daq.bluesky.api.BlueskyController as BlueskyController
from uk.ac.diamond.osgi.services import ServiceProvider
from java.util import Map

from io.blueskyproject import TaggedDocument
from java.util.function import Consumer

class DocConsumer(Consumer):
    
    def __init__(self):
        self.documents = []
        
    def accept(self, value):
        #pass
        #self.documents.append(value.doc())
        print(value)

# Consumer to process bluesky documents emitted during scan and print motor positions
# and detector readout values to Jython console
class BlueskyScanTextOutput(DocConsumer) :
    def __init__(self):
        super(DocConsumer, self).__init__()
        #self.motor_vals = None
        #self.detector_vals = None
        self.all_motor_names = None
        self.all_detector_names = None
        self.bean_filter_type = Map
        self.data_string_format = "%15.4f"
        self.inner_loop_vals = None 
        self.image_uses_demand_vals = True 
        
        self.x_index = 0
        self.y_index = 0;
        self.debug = False
        
    def log(self, message) :
        if self.debug :
            print(message)

    def list_to_string(self, lst, str_format="%15s") :
        return "\t".join( str_format%(val) for val in lst)
        
    #bean_obj = TaggedTocument
    def accept(self, tagged_doc):
        # print(tagged_doc)
        
        event_type = tagged_doc.name().strip()
        event_doc = tagged_doc.doc()
        
        #print(bean_obj)
        #print("Event type : "+event_type)
        if event_type == "start" :
            # print("Motors : "+bean_obj['doc']["motors"])
            print("Start of scan : ")
            self.all_motor_names = event_doc.getMotors()
            self.all_detector_names = event_doc.getDetectors()
            
            print("All motors : %s"%(self.all_motor_names))
            print("All detectors : %s"%(self.all_detector_names))
            
            self.motor_rbv_vals = []
            self.motor_demand_vals = []
            self.detector_vals = []
            print("%s %s"%(self.list_to_string(self.all_motor_names), self.list_to_string(self.all_detector_names)))
        
        if event_type == "event" :
            #print("Event")
            data = event_doc.getData()
            
            self.log("Data : %s"%(data))

            readback_vals = [data[motor_name] for motor_name in self.all_motor_names]
            demand_vals = [data[motor_name] for motor_name in self.all_motor_names]
            self.log("Readback : %s , demand : %s"%(readback_vals, demand_vals))
            
            self.motor_demand_vals.append(demand_vals)
            self.motor_rbv_vals.append(readback_vals)
            
            det_data_names = []
            for name in self.all_detector_names :
                found_name = next(n for n in data.keys() if n.startswith(name))
                if found_name is not None :
                    det_data_names.append(found_name)
            
            self.log("Detector name : %s"%(det_data_names))
            #det_vals = data[det_name]
            det_vals = [data[det_name] for det_name in det_data_names]
            self.log("Detector vals : %s"%(det_vals))
            self.detector_vals.append(det_vals)
            
            # print("%s \t%s"%(motor_vals, det_vals))
            print("%s %s"%(self.list_to_string(readback_vals, self.data_string_format), 
                           self.list_to_string(det_vals, self.data_string_format)))



run 'gdascripts/blueskyHandler.py'

# add event listener to bluesky controller        

executor = ServiceProvider.getService(BlueskyController)
executor.removeWorkerEventListeners() # clear all the listeners

txt_consumer = BlueskyScanTextOutput()
txt_consumer.debug = False
executor.addEventListener(TaggedDocument, txt_consumer) 

"""
'count' plan : 
run_plan("count", detectors=["d7diode"], num=5)

1d line scan : 
run_plan("step_scan", {"detectors" : ["sim_gauss_det"], "motor":"dummy_motor1", "scan_args":[-2.0, 3.0, 21]})

2d grid scan
run_plan("grid_scan", {"detectors" : ["sim_2d_gauss_det"], "motor1":"dummy_motor2", "scan_args1":[-2.0, 2.0, 21], "motor2":"dummy_motor1", "scan_args2":[-1,1,21], "snake_axes":1})
"""

def remove_subscriber() :
    print("Removing EventService listeners")
    executor.removeWorkerEventListener(txt_consumer)
    
add_reset_hook(remove_subscriber)
