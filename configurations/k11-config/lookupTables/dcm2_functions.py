# modified Hans 27/01/2020
import math
from gda.epics.CAClient import get as caget
from gda.epics.CAClient import put as caput
import scisoftpy as dnp

def dcm2_y_in(energy):
    # IF dcm2 is not in operational range in y, move dcm2 to nominal "in", else leave where it is
    y_pos_allowed = [11.5,11.9]
    y_pos_nominal = 11.7
    y_pos_current = dcm2_y.getPosition()
    if y_pos_current < y_pos_allowed[0] or y_pos_current > y_pos_allowed[1]:
        return y_pos_nominal
    else:
        return y_pos_current

def dcm2_y_out(energy):
    # might need this eventually...
    return -11.9

def dcm2_bragg_out(energy):
    return 0

def dcm2_bragg_position(energy): # dcm1 and dcm2 might have slightly different offset in Bragg
    d = 3.1356 # Si 111 spacing
     # calibration of bragg angle versus energy is done by a 3rd degrtee polinomial.
    # To get the proper angle, we first calculate a "modified energ" from the real request 
    # energy. This Emod is then input into the bragg equation to get the request theta
    # to send to the DCM
    p = dnp.array([ 0.0021902 ,  1.01098374, -0.15377086])
    Emod = p[0]*energy**2 + p[1]*energy + p[2]
    theta1 = math.asin(12.398/Emod/2/d)
    theta1 = math.degrees(theta1) # can add possible offset here
    return -theta1 # Attention, Bragg angle is negative on our setup

def dcm2_z_position(energy):
    s = 7.6 # crystal gap mm
    w = 2.2 # beam width mm
    theta1 = -dcm2_bragg_position(energy)
    theta1 = math.radians(theta1)
    z1 = s/math.tan(theta1) - w/math.tan(theta1)
    # z1*0.9 # leave this commented, should be fine without the 10% reduction
    z1 = min([z1,100.2])
    return z1 

def dcm2_roll_position(energy):
    # might leave this hardcoded for now, will need to come up with a good way later
    # roll is some sort of function of E, likely can be arrpoximated with first or even better second order polynomial
    dcm2_roll_coeff01 = -0.008571428571428773 # -1.07143e-3
    dcm2_roll_coeff02 = 0.7285714285714419 # 5.13929e-1
    dcm2_roll_coeff03 = 224.97142857142848 # 3.27807e2
    dcm2_roll_request = dcm2_roll_coeff01*energy**2 + dcm2_roll_coeff02*energy + dcm2_roll_coeff03
    return dcm2_roll_request

def dcm2_pitch_position(energy):
    # we need to scan dcm2_pitch in a reasonable range to get the position with maximum intensity
    # wht do we use as return value??
    # make sure FE shutter is closed
    fe_shutter_status = fe_shutter.getPosition()
    if fe_shutter_status != 'Close':
        print "fe_shutter is not closed, closing"
        fe_shutter('Close')
    else:
        print "fe_shutter is closed"
    # move d2 in
    print "moving d2 in"
    d2_position('Set In beam')
    print "d2 is in beam"
    # on d2, we select ROI around where the mono diffraction beam is
    # first we need to store the current positions so we can return to them later
    reg_start_x_old = int(caget('BL11K-DI-PHDGN-02:ROI:MinX_RBV')) # 0
    reg_size_x_old = int(caget('BL11K-DI-PHDGN-02:ROI:SizeX_RBV')) # 4112
    reg_start_y_old = int(caget('BL11K-DI-PHDGN-02:ROI:MinY_RBV')) # 400
    reg_size_y_old = int(caget('BL11K-DI-PHDGN-02:ROI:SizeY_RBV')) # 1200
    # now set the new roi (need refining this)...
    reg_start_x_new = (4112-1634-132)
    reg_size_x_new = 132*3
    reg_start_y_new = (reg_start_y_old+356-86)
    reg_size_y_new = 86*3
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
    scan(dcm2_pitch, 38.0, 46, 0.1, d2_det, 0.2) # 0.5 seconds should be an appropriate time? depends on energy...
    # now we have the problem of finding the max?
    dcm2_pitch_max_I_pos = maxval.result.maxpos
    # we can turn statistics off on d2 again
    d2_det.computeStats = False
    # close fe shutter
    fe_shutter('Close')
    # gp back to old ROI settings
    caput('BL11K-DI-PHDGN-02:ROI:MinX',reg_start_x_old)
    caput('BL11K-DI-PHDGN-02:ROI:SizeX',reg_size_x_old)
    caput('BL11K-DI-PHDGN-02:ROI:MinY',reg_start_y_old)
    caput('BL11K-DI-PHDGN-02:ROI:SizeY',reg_size_y_old)
    # move d2 out
    print "moving d2 out"
    d2_position('Get Out beam')
    print "d2 is out of beam"
    # return request position
    return dcm2_pitch_max_I_pos