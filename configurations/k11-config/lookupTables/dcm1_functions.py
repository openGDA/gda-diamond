# modified Hans 27/01/2020
import math

def dcm1_y_in(energy):
    # IF dcm1 is not in operational range in y, move dcm1 to nominal "in", else leave where it is
    y_pos_allowed = [9.1,9.3]
    y_pos_nominal = 9.2
    y_pos_current = dcm1_y.getPosition()
    if y_pos_current < y_pos_allowed[0] or y_pos_current > y_pos_allowed[1]:
        return y_pos_nominal
    else:
        return y_pos_current

def dcm1_y_out(energy):
    # might need this eventually...
    return -11.9

def dcm1_bragg_position(energy): # dcm1 and dcm2 might have slightly different offset in Bragg
    d = 3.1356 # Si 111 spacing
    theta1 = math.asin(12.398/energy/2/d)
    theta1 = math.degrees(theta1) # can add possible offset here
    return -theta1 # Attention, Bragg angle is negative on our setup

def dcm1_z_position(energy):
    s = 7.6 # crystal gap mm
    w = 2.2 # beam width mm
    theta1 = -dcm1_bragg_position(energy)
    theta1 = math.radians(theta1)
    z1 = s/math.tan(theta1) - w/math.tan(theta1)
    return z1*0.9

def dcm1_roll_position(energy):
    # might leave this hardcoded for now, will need to come up with a good way later
    # roll is some sort of function of E, likely can be arrpoximated with first or even better second order polynomial
    p2 = -4.0e-03
    p1 = -1.3e-01
    p0 =  6.315
    dcm1_roll_demand = p2*energy**2 + p1*energy + p0
    return dcm1_roll_demand

#!!!!!!!
# Will need a LUT or some other way of inputing one value for a starting position of dcm pitch to scan around
#!!!!!!!



def dcm1_pitch_position(energy):
    # we need to scan dcm1_pitch in a reasonable range to get the position with maximum intensity
    # wht do we use as return value??
    
    # enable collection of statistics on the pco
    pco_addetector.computeStats=True
    # set the axis to evaluate
    rscan.yaxis = 'total' # this sets the total intensity recorded by the pco to be analysed and plotted by default
    # the DCM pitch must be roughly positioned around the optimum position, as we cannot perform scans that are too long...
    dcm1_pitch_current_position = dummy_dcm1_pitch.getPosition() # not needed?
    # perform scan around pitch
    rscan(dummy_dcm1_pitch, -2, 2, 0.05, pco_addetector, 0.1) # Douglas added an exposure for the scan to make sense
    # get the pitch position with max intensity
    dcm1_pitch_max_I_pos = maxval.result.maxpos
    # these are also stored in the .nxs file under /entry1/pco_addetector/total
    # enable collection of statistics on the pco
    pco_addetector.computeStats=False
    # return
    return dcm1_pitch_max_I_pos
