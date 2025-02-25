from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
from test.test_contains import seq
from gda.device.detector.nxdetector import BufferedNXDetector

from gda.device.motor import DummyMotor
from gda.device.scannable import ScannableMotor


def create_dummy_scannable(name):
    mot = DummyMotor()
    mot.setMaxSpeed(100000)
    mot.setName(name+"_motor")
    mot.configure()
    
    dummy_scannable_mot = ScannableMotor()
    dummy_scannable_mot.setName(name)
    dummy_scannable_mot.setMotor(mot)
    dummy_scannable_mot.setSpeed(10000)
    dummy_scannable_mot.configure()
    
    return dummy_scannable_mot


# test_motor=DummyScannable("testmotor")

test_motor = create_dummy_scannable("dummy_scannable_motor")
cont_scannable = QexafsTestingScannable()
cont_scannable.setName("cont_scannable")
cont_scannable.setDelegateScannable(test_motor)
cont_scannable.setMaxMotorSpeed(10000)
cont_scannable.configure()


from gda.scan import ContinuousScan

# deadtime between frames sent by Tfg
frame_dead_time=0.01

def continuous_scan(num_points, time_per_point, *detectors) :
    """
    Do a continuous scan by sending a stream of TTL pulses using Tfg.
    * Scan has num_points pulses
    * Each pulse is separated by small gap; gap duration = 'dead time' 
    (this is needed for some detectors so they have time to readout before next pulse is sent)
    * Each TTL pulse has duration: live time = time_per_point - dead time
    
    total scan duration = num_points*time_per_point = num_points*(live time + dead time )
    """
    qexafs_ionchambers = qexafs_I1
    
    dets = list(detectors)
    
    frame_live_time = time_per_point-frame_dead_time
    
    # append qexafs_counterTimer01 (at end, so other detectors are prepared and armed first)
    if qexafs_ionchambers not in dets :
        dets.append(qexafs_ionchambers)
        
    # Set the collection time on each detector to match the live time
    # (this shouldn't make a difference if hardware trigger length determines frame length)
    #for d in detectors : 
    #    if isinstance(d, BufferedNXDetector) :
    #        d.getCollectionStrategy().setCollectionTime(frame_live_time)
    # 4/2/2/2025 : this causes problems for subsequent medipix step scans with tfg if time per point is < collectionStrategy.collectionTime 
    # Symptom is scan waits forever for when waiting for first point, frame counter never increment.
    # --> to avoid problems, make collectionTime < typical time per point (default is 0.1 sec for medipix)

    total_time = num_points*frame_live_time
    print("Time per point : {}, total time : {}".format(time_per_point, total_time))
    
    # Make sure that Tfg is not waiting for an external trigger to start
    qexafs_ionchambers.setUseExternalTriggers(False)
    qexafs_ionchambers.setFrameDeadTime(frame_dead_time)

    cont_scan=ContinuousScan(cont_scannable, 0, num_points, num_points, total_time, dets)
    return cont_scan

def get_tfg_pulse_triggers(usr_outputs_list, pulse_length=0.01, pulse_gap=0.0) :
    """ 
    Generate Tfg command to send series of pulses on usr output ports. Each pulse has same length
    Parameters :
        usr_outputs_list - list of ports to send pulses on. e.g. [1,2] - sends pulses on usr0 then usr1
        pulse_length - length of each pulse (seconds)
    Returns :
        String containing trigger commands
    """
    triggers=""
    for output in usr_outputs_list :
        triggers+="1 0.0 %.6f 0 %d 0 0\n"%(pulse_length, output)
        if pulse_gap > 0.0 :
            triggers+="1 0.0 %.6f 0 0 0 0\n"%(pulse_gap)
    return triggers

def reset_valves() :
    """
        Switch both valves off (by sending pulse to USR0 and USR1 at same time)
    """
    switch_valve_positions([3])

def switch_valve_positions(usr_outputs_list, pulse_length=0.01) :
    """ 
    Send series of pulses on usr output ports of Tfg. Each pulse has same length
    Parameters :
        usr_outputs_list - list of ports to send pulses on. e.g. [1,2] - sends pulses on usr0 then usr1
        pulse_length - length of each pulse (seconds)
    """
    group="tfg setup-groups\n1 0.0000000 0.0 0 0 0 0\n"
    start_tfg = "-1 0 0 0 0 0 0\ntfg arm\ntfg start\n"
    triggers=get_tfg_pulse_triggers(usr_outputs_list, pulse_length)

    DAServer.sendCommand(group+triggers+start_tfg)

from gda.device.scannable import ScannableBase

class TfgTriggerPreparer(ScannableBase):
    
    def __init__(self,name):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%s'])
        
        # dict of trigger sequences (one = usr1 then usr0, two = usr0 then usr1 etc)
        self.sequences = { "one" : [2,1], "two":[1,2], "initial":[1], "none":[]}
        self.reset_seq = [3]
        
        self.reset_sleep_time = 1 # low long to wait for after resetting valve state at start of scan
        self.first_after_reset = True
        self.sequence = None
        self.buffered_scaler = None
        self.pausetime_after_switch = 0.0


    def atScanStart(self):
        self.reset()
    
    def atScanEnd(self):
        self.reset()
    
    def atCommandFailure(self):
        self.reset()
          
    def reset(self) :
        print("Sending command to reset valve state")
        reset_valves()
        self.first_after_reset = True
        print("Waiting {} seconds...".format(self.reset_sleep_time))
        sleep(self.reset_sleep_time)

    def getPosition(self):
        return str(self.sequence)
    
    def asynchronousMoveTo(self, sequence_string):
        """
        Set buffered_scaler#setGroupInitialCommand to include additional
        lines to produce the usr0, usr1 triggers
        """
        if sequence_string.lower() in self.sequences :
            seq = self.sequences[sequence_string]
            
            # very first time after reset, just need single pulse on usr0
            if self.first_after_reset :
                seq = self.sequences["initial"]
                
            pulse_commands = get_tfg_pulse_triggers(seq)
            
            #insert gap after switching
            if float(self.pausetime_after_switch) > 0.0 :
                pulse_commands+="1 0.0 %.6f 0 0 0 0\n"%(float(self.pausetime_after_switch))
    
            self.buffered_scaler.setGroupInitialCommand(pulse_commands)
            self.sequence = seq
            #print("{} : {} (tfg triggers = {})".format(sequence_string, seq, pulse_commands))
        else :
            print("Cannot move to {} - position not recognized".format(sequence_string))
            
        self.first_after_reset = False

    def isBusy(self):
        return False

trigger_preparer=TfgTriggerPreparer("trigger_preparer")
trigger_preparer.buffered_scaler = qexafs_I1

"""
Procedure :

send usr0+usr1 (reset positions, 1 and 2 both off) before scan (and wait for a bit for lines to clear?)

change energy

    send usr0 (switch 1 on first point)
    measure n frames
    
    send usr0, usr1 (switch 1 off, switch 2 on) 
    measure n frames
    
    send usr1, usr0 (switch 2 off, switch 1 on)
    measure n frames
    
    send usr0, usr1 (switch 1 off, switch 2 on)
    measure n frames    
    ...
    
change energy

    send usr1, usr0 (switch 2 off, switch 1 on) 
    measure n frames
    
    send usr0, usr1 
    measure n frames

etc

Send 'reset' at the end of the scan (or if scan fails or is aborted)

"""

"""
A TfgTriggerPreparer scannable is used to send the triggers to usr0 and usr1, then stream of pulses to trigger
collection on medipix detectors and ionchambers. The positions 'one', 'two' are used to switch between valve
1 and 2 being open by sending pulses to usr0 and usr1 in the correct order.

scan atn1 ("Filter 1", "Filter 2") trigger_preparer ("one", "two", "one", "two") test 0 10 1.0 ionchambers 0.1

NB : 'frame dead time' should be set on the bufferScaler - to avoid sending next trigger whilst medipix is reading out data
s.g.
    qexafs_counterTimer01.setFrameDeadTime(0.01)
seems appropriate. Exposure time in Epics when using hardware triggered mode is not relevant (i.e. ignored by detector and- 
collection time is determined by length of hardware trigger signal).

BUT : qexafs_medipix1.getCollectionStrategy().setCollectionTime(0.01) # sets detector exposure in Epics at start of scan - it
seems to affect how fast can scan, even though it shouldn't affect anything?

Working example :
qexafs_counterTimer01.setFrameDeadTime(0.01)
scan trigger_preparer ("one", "two", "one", "two") continuous_scan(10, 0.25, qexafs_medipix1)
scan trigger_preparer ("one", "two", "one", "two") continuous_scan(10, 0.01, qexafs_medipix1)



scan bragg1 7114.8 7115.8 0.5 trigger_preparer ('one', 'two') cont_scannable 0.0 120.0 120 118.8 qexafs_medipix1 qexafs_I1
scan bragg1 7110 7117 0.2 trigger_preparer ('one', 'two') cont_scannable 0.0 150.0 150 223.5 qexafs_medipix1 qexafs_I1
see error : 24/1/2025 15:22 
"""

