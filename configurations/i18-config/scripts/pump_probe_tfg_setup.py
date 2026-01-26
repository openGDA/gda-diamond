converter = finder.find("auto_mDeg_idGap_mm_converter_Si111")

run 'qexafs_scans.py'
run 'laser_exp_processor.py'

print "Starting script..."

#------------------------------
#  START OF USER BIT

noOfReps = 50 #number of repetitions of cycles
noOfCycles = 200000 #number of cycles at each energy value (laser pulses)
noOfFrames = 190 #number of frames in a cycle
collectionTime = 375e-9  #data collection time for each frame, sec.
deadTime = 0#dead time between frames
delayAfterTrigger = 0 #delay after receiving trigger when the Tfg starts time frames

time_between_triggers = 0*1.0/53.3e3 # 53.3kHz triggers
buffered_scaler.delay_after_laser_on_trig = 0 # time_between_triggers - 250e-9 # 18.4e-6   # delay until next 25kHz pulse - minus a bit
buffered_scaler.delay_after_laser_off_trig = 0 #5e-6

# 8 = TTL0, 9 = TTL1, 10, TTl2 etc. 0 = don't wait for trigger
buffered_scaler.laser_on_trig_port = 10 # trigger on rising edge of TTL2
buffered_scaler.laser_off_trig_port = 0 

# Frame ranges for pump on ,  off data
laser_exp_processor.start_frame_range = 0,1 # likely this pump_on
laser_exp_processor.end_frame_range = 38,39  # likely the pump_off

laser_exp_processor.detector_name = buffered_scaler.getName()
laser_exp_processor.apd_data_name = "/Iapd"


"""Example of manually reprocessing data : 
First adjust the start and end frame ranges if required :  

    laser_exp_processor.start_frame_range =  0,10
    laser_exp_processor.end_frame_range = 50,60

Call 'laser_exp_processor.add_processed_data' function to reprocess the data and pass it the full path to the nxs file. 
Also set overwrite to True to overwrite any processed data that was previously written. For example :

    laser_exp_processor.add_processed_data("/dls/i18/data/2024/sp28407-1/nexus/224250_i18.nxs", overwrite=True)
"""

outputDir = ""

#--------------------------------
#XANES energy regions setup
#----------------------------------
"""
XANES_regions=  { # (energyValue, energy_step, num_points)  
    'r1': (13380, 10, 3),
    'r2': (13415, 5, 5), 
    'r3': (13441, 1, 64), 
    'r4': (13510, 5, 6),
    'r5': (13550, 7, 7),
    }
"""
"""
#Co edge
XANES_regions=  { # (energyValue, energy_step, num_points)  
     'r1': (7670, 2, 20),
     'r2': (7710, 1, 15), 
     'r3': (7725, 2, 25), 
     #'r4': (7731, 1, 16),
     #'r5': (7747, 2, 11),
     }
""

"""
#Mn edge
XANES_regions=  { # (energyValue, energy_step, num_points)  
     'r1': (6500, 2, 15),
     'r2': (6530, 1, 5), 
     'r3': (6535, 0.5, 51), 
     'r4': (6561, 1, 16),
     'r5': (7747, 2, 11),
     }
"""
XANES_regions=  { # (energyValue, energy_step, num_points)  
     'r1': (4952, 1, 3),
     'r2': (4962, 1, 2), 
     'r3': (4993, 1, 4), 
     'r4': (13080, 5, 6),
     'r5': (13120, 10, 5),
"""  

tfgScanRunner.initial_group_command=""
tfgScanRunner.external_trigger_frames = False
tfgScanRunner.external_trigger_start = False
tfgScanRunner.frame_dead_time = deadTime
tfgScanRunner.num_cycles = noOfCycles


#--------------------------------
#XANES energy regions setup complete
#----------------------------------
energyPos=[]
region_num = len(XANES_regions)

# Make list of energies for XANES regions 
# (need to do it like this since Python2 dicts are unsorted!)
for section in range(region_num):
    region_vals = XANES_regions['r'+str(section+1)]
    energyValue, energy_step, num_points = region_vals[0], region_vals[1], region_vals[2]
    for i in range(num_points):
        energyPos.append(energyValue)
        energyValue += energy_step

#------------------------------
#  END OF USER BIT 
#------------------------------

# Select the 'nogap' version of DCM energy scannable if beam is not available
energy_scannable = energy if beam_available() else energy_nogap

print("Energy scannable : {}".format(energy_scannable.getName()))
print("XANES energies  : {}".format(energyPos))

converter.enableAutoConversion()  
energy_scannable.moveTo(energyPos[0])

# set input name so energy values are correctly labelled in ascii file
energy_scannable.setInputNames(['energy'])

for kk in range(noOfReps):
    print("Running repetition %d"%(kk))
    
    name_format = "/%d_"+str(kk)
    tfgScanRunner.nexus_name_template = outputDir+"/nexus/"+name_format+".nxs"
    tfgScanRunner.ascii_name_template = outputDir+"/ascii/"+name_format+".dat"
    scan energy_scannable tuple(energyPos) tfgScanRunner.generate_scan(noOfFrames, collectionTime)
    try:
        laser_exp_processor.add_processed_data(lastScanDataPoint().getCurrentFilename(), overwrite=True)
    except:
        print("Could not calculate processed data.")

print("Script finished")
