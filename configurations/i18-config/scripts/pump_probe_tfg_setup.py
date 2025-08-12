from gda.epics import CAClient
from time import sleep
import time
converter = finder.find("auto_mDeg_idGap_mm_converter_Si111")

run 'qexafs_scans.py'
run 'laser_exp_processor.py'

print "Starting script..."
energyPos = []


#------------------------------
#  START OF USER BIT 

noOfReps = 200 #number of repetitions of cycles
noOfCycles = 200000 #number of cycles at each energy value (laser pulses)
noOfFrames = 124 #number of frames in a cycle
collectionTime = 250e-9 #data collection time for each frame, sec.
deadTime = 0.0 #dead time between frames
delayAfterTrigger = 0 # delay after receiving trigger when the Tfg starts time frames

tfgScanRunner.buffered_scaler = buffered_scaler

# Frame ranges for pump on , off data
laser_exp_processor.apd_data_name = "It"
laser_exp_processor.detector_name = "buffered_scaler"
laser_exp_processor.start_frame_range = 0,1
laser_exp_processor.end_frame_range = 50,60

"""Example of reprocessing data : 
Adjust the ranges if required :  

    laser_exp_processor.start_frame_range =  0,10
    laser_exp_processor.end_frame_range = 50,60

Call 'add_processed_data' function to reprocess the data : needs full path to the nxs file, overwrite to True to overwrite any processed data that was previously written :

    laser_exp_processor.add_processed_data("/dls/i18/data/2024/sp28407-1/nexus/224250_i18.nxs", overwrite=True)
"""

outputDir = ""


#--------------------------------
#XANES energy regions setup
#----------------------------------

XANES_regions=  { # (energyValue, energy_step, num_points)  
    'r1': (6520, 2, 5), 
    'r2': (6530, 1, 5), 
    'r3': (6535, 0.5, 51),
    'r4': (6561, 1, 16),
    }
test_region = {
    'r1' : (10000, 1, 5)
    }

#XANES_regions = test_region

buffered_scaler.delay_after_laser_on_trig = 2e-6
buffered_scaler.delay_after_laser_off_trig = 2e-6
buffered_scaler.laser_on_trig_port = 8 # trigger on rising edge of ttl0
buffered_scaler.laser_off_trig_port = 9 # trigger on rising edge of ttl1 

# tfgScanRunner.initial_group_command = "1 %.5g 0 0 0 8 0"%(delayAfterTrigger)
tfgScanRunner.initial_group_command=""
tfgScanRunner.external_trigger_frames = False
tfgScanRunner.external_trigger_start = False
tfgScanRunner.frame_dead_time = deadTime
tfgScanRunner.num_cycles = noOfCycles


#--------------------------------
#XANES energy regions setup complete
#----------------------------------

region_num = len(XANES_regions) 
for section in range(region_num):      
    energyValue, energy_step, num_points = XANES_regions['r'+ str(section+1)][0], XANES_regions['r'+ str(section+1)][1], XANES_regions['r'+ str(section+1)][2]
    for i in range(num_points):
        energyPos.append(energyValue)
        energyValue += energy_step

#------------------------------
#  END OF USER BIT 
#------------------------------
print(energyPos)

converter.enableAutoConversion()  
energy.moveTo(energyPos[0])


# set input name so energy values are correctly labelled in ascii file
energy.setInputNames(['energy'])

for kk in range(noOfReps):
    print("Running repetition %d"%(kk))
    
    name_format = "/%d_"+str(kk)
    tfgScanRunner.nexus_name_template = outputDir+"/nexus/"+name_format+".nxs"
    tfgScanRunner.ascii_name_template = outputDir+"/ascii/"+name_format+".dat"
    scan energy tuple(energyPos) tfgScanRunner.generate_scan(noOfFrames, collectionTime)
    try:
        laser_exp_processor.add_processed_data(lastScanDataPoint().getCurrentFilename(), overwrite=True)
    except:
        print("Could not calculate processed data.")

print("Script finished")
