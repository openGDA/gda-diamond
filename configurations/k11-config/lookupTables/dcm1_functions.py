# modified Hans 27/01/2020
import math
from gda.epics.CAClient import get as caget
from gda.epics.CAClient import put as caput

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

def dcm1_bragg_out(energy):
    return 0

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
    # z1*0.9 # leave this commented, should be fine without the 10% reduction
    z1 = min([z1,103])
    return z1 

def dcm1_roll_position(energy):
    # might leave this hardcoded for now, will need to come up with a good way later
    # roll is some sort of function of E, likely can be arrpoximated with first or even better second order polynomial
    dcm1_roll_coeff01 = -2.444 # -2.03392857
    dcm1_roll_coeff02 = -190.787 # -242.85357143
    dcm1_roll_request = dcm1_roll_coeff01*energy + dcm1_roll_coeff02
    return dcm1_roll_request

#!!!!!!!
# Will need a LUT or some other way of inputing one value for a starting position of dcm pitch to scan around
#!!!!!!!



def dcm1_pitch_position(energy):
    # we need to scan dcm1_pitch in a reasonable range to get the position with maximum intensity
    # wht do we use as return value??
    # make sure FE shutter is closed
    fe_shutter_status = fe_shutter.getPosition()
    if fe_shutter_status != 'Close':
        fe_shutter('Close')
    # move d2 in
    d2_position('Set In beam')
    # define exposure time
    exp_time = 0.2
    
    # on d2, we select ROI around where the mono diffraction beam is
    # first we need to store the current positions so we can return to them later
    reg_start_x_old = int(caget('BL11K-DI-PHDGN-02:ROI:MinX_RBV')) # 0
    reg_size_x_old = int(caget('BL11K-DI-PHDGN-02:ROI:SizeX_RBV')) # 4112
    reg_start_y_old = int(caget('BL11K-DI-PHDGN-02:ROI:MinY_RBV')) # 400
    reg_size_y_old = int(caget('BL11K-DI-PHDGN-02:ROI:SizeY_RBV')) # 1200
    # now set the new roi (need refining this)...
    reg_start_x_new = (4112-2084-157)
    reg_size_x_new = 157*3
    reg_start_y_new = (reg_start_y_old+440-100)
    reg_size_y_new = 100*3
    # set in epics
    caput('BL11K-DI-PHDGN-02:ROI:MinX',reg_start_x_new)
    caput('BL11K-DI-PHDGN-02:ROI:SizeX',reg_size_x_new)
    caput('BL11K-DI-PHDGN-02:ROI:MinY',reg_start_y_new)
    caput('BL11K-DI-PHDGN-02:ROI:SizeY',reg_size_y_new)
    # some preparation for D2
    # set collecting statistics to True, and select total intensity as the returned variable
    d2_det.computeStats = True
    scan.yaxis = 'total'
    # open fe shutter
    fe_shutter('Open')
    # then we can run a scan, we know the approximate pitch positions
    scan(dcm1_pitch, -106.0, -102, 0.1, d2_det, exp_time) # 0.5 seconds should be an appropriate time? depends on energy...
    # now we have the problem of finding the max?
    dcm1_pitch_max_I_pos = maxval.result.maxpos
    # we can turn statistics off on d2 again
    d2_det.computeStats = False
    # this is approximate, but should do for now, now we move there
    # close fe shutter
    fe_shutter('Close')
    # gp back to old ROI settings
    caput('BL11K-DI-PHDGN-02:ROI:MinX',reg_start_x_old)
    caput('BL11K-DI-PHDGN-02:ROI:SizeX',reg_size_x_old)
    caput('BL11K-DI-PHDGN-02:ROI:MinY',reg_start_y_old)
    caput('BL11K-DI-PHDGN-02:ROI:SizeY',reg_size_y_old)
    # move d2 out
    d2_position('Get Out beam')
    # return request position
    return dcm1_pitch_max_I_pos