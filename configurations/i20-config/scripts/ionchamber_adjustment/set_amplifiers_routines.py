###########
# Ionchamber sensitivty adjustment script. Adapted from B18 and heavily modified and refactored to facilitate reuse on other beamlines
#

from time import sleep
from warnings import warn
import random

print("\nRunning 'ionchamber_adjustment/set_amplifiers_routines.py'")


# lists for convert between value and index (0~35)
val_list=['1','2','5','10','20','50','100','200','500']
scale_list=['pA/V','nA/V','uA/V','mA/V']

I0_NAME, IT_NAME, IREF_NAME, I1_NAME = "i0", "it", "iref", "i1"
LOW, HIGH, OK, OPTIMIZED = "low", "high", "ok", "optimized"

# Sensitivity and unit controls for each ionchamber
sensitivity_controls = { I0_NAME : [i0_stanford_sensitivity, i0_stanford_sensitivity_units],
                IT_NAME : [it_stanford_sensitivity, it_stanford_sensitivity_units],
                IREF_NAME : [iref_stanford_sensitivity, iref_stanford_sensitivity_units],
                I1_NAME : [i1_stanford_sensitivity, i1_stanford_sensitivity_units] }

all_sensitivity_controls = sensitivity_controls[I0_NAME], sensitivity_controls[IT_NAME], sensitivity_controls[IREF_NAME], sensitivity_controls[I1_NAME]

LOG_LEVEL=0
def debug(msg):
    global LOG_LEVEL
    if LOG_LEVEL == 1 :
        print("   "+msg)

def indexToValue(ampl): # ampl is 0~35
    def scale():
        return int(ampl/9)
    def val():
        return int(ampl-scale()*9)
   
    #return [val_list[val()],scale_list[scale()]]
    return [val(),scale()]

def get_amp_txt(amp_int):
    scale_int=amp_int//9
    val_int=amp_int%9
    scale_txt=scale_list[scale_int]
    val_txt=val_list[val_int]
    return val_txt+scale_txt

def get_counts_status(count_rates, max_I, min_I):
    """
        Check the count rates and return list containing status of each one :
            HIGH - if count > max_I
            LOW - if count < min_I
            OK - count is between low and high limits
        
        Parameters :
            count_rates - list of counts from ionchambers
            max_I - maximum allowed count rate
            min_I - miniumum allowed count rate
            
    """
    ic_status=[]
    for counts in count_rates:
        if counts > max_I:
            ic_status.append(HIGH)
        elif min_I <= counts <= max_I:
            ic_status.append(OK)
        elif counts < min_I:
            ic_status.append(LOW)
        else:
            ic_status.append('error_reading_detector_values')
    return ic_status

def read_chambers(ionchamber_ref, collection_time=1.0):
    ionchamber_ref.setCollectionTime(collection_time)
    ionchamber_ref.collectData()
    sleep(collection_time*1.1)
    return ionchamber_ref.readout()

# Convert sensitivity and scale value to single number (0 ... 30)
def valueToIndex(val, scale): 
    ampl=int(val_list.index(val))+int(scale_list.index(scale))*9
    return ampl

def read_single_ampl(sens_control, sens_unit_control): # index
    val1= sens_control.getPosition() 
    scale1= sens_unit_control.getPosition()

    #convert the text code for amplification+scale into a number 
    ampl1=valueToIndex(val1, scale1)

    debug('Amplifier value index for {}, {} : {}'.format(sens_control.getName(), sens_unit_control.getName(), ampl1))
    return ampl1


def set_single_ampl(sens_control, sens_units_contol, ampl_value): #ampl_arr is index array
    # Convert single number into value and scale values
    val_index, scale_index = indexToValue(ampl_value)
    val_demand = val_list[val_index]
    scale_demand = scale_list[scale_index]
    #
    debug("Amplifier combined value : {}".format(ampl_value))
    debug("Adjusting amplifiers : {} = {}, {} = {}".format(sens_control.getName(), val_demand, sens_units_contol.getName(), scale_demand))
    sens_control.moveTo(val_demand)
    sens_units_contol.moveTo(scale_demand)
    return val_demand, scale_demand

def set_ampl(controls_list, ampl_values_list): #ampl_arr is index array
    for ctrl, ampl_value in zip(controls_list, ampl_values_list) :
        set_single_ampl(*ctrl, ampl_value=ampl_value)

def get_short_name(stanford_ampl_object):
    fullname = stanford_ampl_object.getName()
    underscore_pos = fullname.index("_")
    return fullname[:underscore_pos]


def set_amplifier_sensitivities(amplifier_names, ind_vals) :
    for amp_name, amp_value in zip(amplifier_names, ind_vals) :
        print("Setting amplifers for {} to {} ({})".format(amp_name, get_amp_txt(amp_value), amp_value))
        set_single_ampl(sensitivity_controls[amp_name][0], sensitivity_controls[amp_name][1], amp_value)

def adjust_sensitivities(amplifier_names, ionchamber_ref=ionchambers, min_I=250000.0, max_I=800000.0):
    """
        Adjust sensitivities of stanford amplifiers, so that count rate for each
        channel of ionchamber is with acceptable range (i.e. between min_I and max_I counts)
        limit determined by 'get_counts_status' function).
        Warning are shown if :
            count rate is too high and amplification is at minimum;
            count rate is too low and amplification is at maximum
            
        Parameters : 
            amplifier_names - a list containing names of amplifiers that should be adjusted
                        e.g. "i0", "it", "iref"
            
            ionchamber_ref - ionchamber detector object that collects data on ionchambers and returns 
                        an array of i0, it, iref, i1 counts
            
            min_I    minimum acceptable ionchamber counts (default = 250000)
            max_I    maximum acceptable ionchamber counts (default = 800000)
        Return :
            list of amplifier sensitivities (indices between 0 and 35 inclusive)
    """

    print("Target ionchamber count range : {} ... {}".format(min_I, max_I))
    
    def keep_values(ic):
        amplifier_new_value[ic]=amplifier_value[ic]
        
    def optimise_low_counts(ic):
        # increase gain by 1 or 2 steps
        step = 2 if counts[ic] < min_I else 1
        debug("Low counts : increasing gain by {} steps".format(step))
        amplifier_new_value[ic]=amplifier_value[ic]-step
        
    def optimise_high_counts(ic):
        # reduce gain by 1 or 2 steps
        step = 2 if counts[ic] > max_I else 1
        debug("High counts : reducing gain by {} steps".format(step))
        amplifier_new_value[ic]=amplifier_value[ic]+step
        
    def reduce_to_keep_safe_counts(ic):
        amplifier_new_value[ic]=min(amplifier_value[ic]+1,35)
    
    ionchamber_readout_names = [n.lower() for n in ionchamber_ref.getExtraNames()]
    num_channels = len(ionchamber_readout_names)
    
    # Convert amplifier name string to a list
    if isinstance(amplifier_names, str) :
        amplifier_names = [amplifier_names]

    # Make dictionary with channel index to be used for each of the ionchambers being optimised
    readout_indices = {}
    for name in amplifier_names :
        short_name = get_short_name(sensitivity_controls[name][0]).lower()
        readout_index = ionchamber_readout_names.index(short_name)
        readout_indices[name] = int(readout_index)
    
    print("Reading ionchambers using : {}".format(ionchamber_ref.getName()))    
    print("Ionchamber readout indices : {}".format(readout_indices))
    
    amps_ok=[False]
    amplifier_new_value=[]
    
    old_status=[""]*num_channels
    loop_counter = 0
    
    while amps_ok.count(True) is not len(amplifier_names) and loop_counter < 20 :
        amps_ok=[False]*num_channels
        
        loop_counter=loop_counter+1
        print("\n---- Iteration : {} ----".format(loop_counter))
        sleep(0.1)
        
        # readout sensitivity settings for all the amplifiers (i.e. for all the ionchamber channels)
        amplifier_value=[read_single_ampl(cont[0], cont[1]) for cont in all_sensitivity_controls]
        
        print("Amplification settings  : {}".format([get_amp_txt(amp_int) for amp_int in amplifier_value]))
        
        # Collect ionchamber counts       
        ionchamber_readout=read_chambers(ionchamber_ref)
        counts = list(ionchamber_readout)
        
        print("Ionchamber counts   : {}".format(counts))
        
        # Determine the count status for each channel (high, low, ok)
        ic_status=get_counts_status(counts, max_I, min_I)
        print("Ion chambers count status : {}".format(ic_status))
        
        # Make copy  of the current amplifier values - this will be modified
        # to increase, decrease the gain as required.
        amplifier_new_value=[ampl_val for ampl_val in amplifier_value]
        
        # loop over each amplifier
        for amp_name in amplifier_names:
            
            # Index in ionchamber readout that is controlled by this amplifier
            ic = readout_indices[amp_name]
            
            # Show names of scannables that control the amplifier (for information purposes)
            controls = sensitivity_controls[amp_name]
            print("\nAdjusting ion chamber : {} ({}, {})".format(amp_name, controls[0].getName(), controls[1].getName()))
            
            # check the size of the readout values and adjust the gains
            if ic_status[ic] == OK:
                print("--Count rates are ok")
                keep_values(ic)
                amps_ok[ic]=True
            elif ic_status[ic] == LOW:
                if amplifier_value[ic]==0:
                    print("Low count limit reached and sensitivity at maximum")
                    keep_values(ic)
                    amps_ok[ic]=True
                    warn("\n Ionchamber "+str(ic)+"; Amplification at minimum value, intensities cannot be further optimised")
                elif OK in old_status[ic]:    
                    print("--Counts were ok and then decreased")
                    #counts oscillating around lowest_acceptable_I, no changes in amplification needed
                    keep_values(ic)
                    amps_ok[ic]=True
                else :
                    #run a loop that optimizes the amplifications to be as close as possible to max_I without saturation
                    print('--Running loop to optimize low counts')
                    optimise_low_counts(ic)
                    old_status[ic]=old_status[ic]+"_"+OPTIMIZED
            elif ic_status[ic] == HIGH:
                if amplifier_value[ic]==35:
                    print("--High count limit reached and sensitivity at minimum")
                    keep_values(ic)
                    amps_ok[ic]=True
                    warn("\n Ionchamber "+str(ic)+"; Amplification at maximum value, detector saturation cannot be avoided")
                elif OK in old_status[ic]:
                    print('--Counts were ok and then increased')
                    #counts oscillating around max_I value, one step change applied to stay in a safe count region
                    #ok, no need to double check counts
                    reduce_to_keep_safe_counts(ic)
                    amps_ok[ic]=True    
                elif OPTIMIZED in old_status[ic]:
                    print("--Counts were optimised from low and then saturated")
                    # previous optimization loop did not work, avoid going in infinite loop 
                    #goes down step by step until not saturated
                    reduce_to_keep_safe_counts(ic)
                    amps_ok[ic]=True
                else:    
                    #changes scale unit and optimize during next loop 
                    print("--Running loop to optimize high counts")        
                    optimise_high_counts(ic)
            old_status[ic]=old_status[ic]+'_'+ic_status[ic]
            
        print("Finished adjusting ionchambers\n")
        print("Amplifiers counts ok : {}".format(amps_ok))
        
        debug("Old_status    : {}".format(old_status))
        debug("Applying settings to amplifiers : {}".format(amplifier_new_value))
        
        amp_values = [amplifier_new_value[readout_indices[amp_name]] for amp_name in amplifier_names]
        set_amplifier_sensitivities(amplifier_names, amp_values)
        
    print("\nFinished adjusting ionchambers")
    print("Final ok status : {}".format(amps_ok))
    amplifier_new_value_txt = [get_amp_txt(amp_int) for amp_int in amplifier_new_value]
    print("Final amplification values : {}".format(amplifier_new_value_txt))
    return amplifier_new_value

def adjust_sensitivities_2E(ampl_controls, E1,E2, **kwargs):
    print("Running ionchamber optimisation at {} and {} eV".format(E1, E1))
    print("Moving monochromator to {} eV".format(E1))
    bragg1.moveTo(E1)
    ampl_E1=adjust_sensitivities(ampl_controls, **kwargs)
    
    print("Moving monochromator to {} eV".format(E2))
    bragg1.moveTo(E2)
    ampl_E2=adjust_sensitivities(ampl_controls, **kwargs)

    # Set lowest sensitivity measured
    amp_values=[max(ampl_E1[0],ampl_E2[0]),max(ampl_E1[1],ampl_E2[1]),max(ampl_E1[2],ampl_E2[2])]
    print("Max amplifier values : {}".format(amp_values))
    set_amplifier_sensitivities(ampl_controls, amp_values)
    print 'Finished'
    return
