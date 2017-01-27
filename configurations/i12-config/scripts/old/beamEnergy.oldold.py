from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands.ScannableCommands import *
import scisoftpy as dnp
import time
import math
from gda.factory import Finder

finder = Finder.getInstance()

mc1_bragg=finder.find("mc1_bragg")
mc2_bragg=finder.find("mc2_bragg")
mc2_z=finder.find("mc2_z")
camMono2_y=finder.find("camMono2_y")


try:
    from positionCompareMotorClass import PositionCompareMotorClass
    camMono2_y = PositionCompareMotorClass("camMono2_y", "BL12I-OP-DCM-01:CAM2:Y.VAL", "BL12I-OP-DCM-01:CAM2:Y.RBV", "BL12I-OP-DCM-01:CAM2:Y.STOP", 0.002, "mm", "%.3f")
except:
    print "Failed to create camMono2_y."


def usage():
    print ""
    print "Loading function set_mono_energy()"
    print "Syntax:      set_mono_energy(energy)"
    print "Description: set_mono_energy(energy) returns the desired monochromator motor positions for a desired energy (keV)."


def func_mono_inner(z0, d1, z, *arg):
    a = 50/(z[0]-z0)
    return (dnp.degrees(dnp.arctan(dnp.array([a])))+d1)/2

def func_cam(h, zcam, cam, *arg):
    return ((250 + h + cam[0])/(3200 + zcam))

def func_lambda(d0, dw, T, *arg):
    return 2*d0*dnp.sin(dnp.radians(T[0]))+dw

def func_theta2(c2_error, dummy, c2, *arg):
    return (c2[0] - c2_error) + dummy

def calc_motor(target_wavelength, lam_error, fitted_d0, d1_error, d_spacing, c2_error, height, z_error_forcam, z_cam, h_cam_error):

    target_c1 = dnp.degrees(dnp.arcsin(dnp.array([(target_wavelength - lam_error)/(2*fitted_d0)]))) + d1_error/2
    target_c2 = dnp.degrees(dnp.arcsin(dnp.array([target_wavelength / (2*d_spacing)]))) + c2_error
    target_z = height / dnp.tan(dnp.radians(2*target_c1 - d1_error)) + z_error_forcam
    target_cam = (z_cam * dnp.tan(dnp.radians(2*target_c1 - d1_error))) - h_cam_error
        
    return dnp.array([- target_c1, - target_c2, target_z, target_cam])
    #return -target_c1, -target_c2, target_z, target_cam

def R2(data, fit):    
    SStot = dnp.sum((data - dnp.mean(data))**2);    
    SSerr = dnp.sum((data - fit)**2)   
    return 1 - SSerr/SStot


def moveToBeamEnergy(target_energy):
    
    print "Calculating target positions"
    
    charge = 1.60217646e-19
    planks = 6.626068e-34
    sp_light = 2.99792458e8
    d_spacing = 0.313599
    #height = 50.0
    
    #collected with all 3 jacks set to 0.0, and the benders to 70-71 micrometers
    #c1 = - dnp.array([-2074.1, -1826.9, -1531.9, -1350.1, -1191.0, -1068.3, -956.4, -872.3, -796.7])/1000
    #c2 = - dnp.array([-1921.0, -1672.4, -1382.2, -1205.1, -1046.0, -914.2, -820.4, -734.3, -656.4])/1000
    #z = dnp.array([668.8, 757.5, 896.8, 1010.7, 1137.3, 1263.7, 1390.4, 1516.8, 1643.2])
    #E = dnp.array([53.15, 60.14, 70.15, 80.15, 90.2, 100.36, 110.36, 120.40, 130.49])
    #cam = dnp.array([-22.1, -50.8, -84.0, -104.3, -122.0, -136.0, -147.6, -157.4, -165.2])
    
    #indices = dnp.array([0, 1, 3, 4, 5, 6, 7, 8])
    
    #user offsets
    c1_offset = 290.18
    c2_offset = 927.43
    z_offset = 1900.9
    
    #calibration dial values for c1, c2, an dz
    c1 = - (dnp.array([-2355.9, -1866.5, -1533.0]) + c1_offset)/1000
    c2 = - (dnp.array([-2981.4, -2500.0, -2170.0]) + c2_offset)/1000
    z =  - dnp.array([1204.5, 989.7, 750.0]) + z_offset
    E = dnp.array([55.09, 72.02, 90.98])
    cam = dnp.array([-1, -54.6, -90.7])
    
    indices = dnp.array([0, 1, 2])
    
    
    
    c1 = c1[indices]    
    c2 = c2[indices]    
    z = z[indices]    
    E = E[indices]    
    cam = cam[indices]    
    num = len(E)    
    
    wavelength = ((sp_light * planks / (E * 1e-9)) / charge) / 1000
    theta_theory = dnp.degrees(dnp.arcsin(wavelength / (2*d_spacing)))
    target_wavelength = ((sp_light * planks / (target_energy * 1e-9)) / charge) / 1000  
    
    fit_mono_opt = dnp.fit.fit(func_mono_inner, z, c1, [0,0], [(-30,30),(-1,1)], optimizer='global')
    z_error_forcam = fit_mono_opt[0]
    d1_error = fit_mono_opt[1]
    fitted_c1_forcam = (dnp.degrees(dnp.arctan(50.0/(z-z_error_forcam)))+d1_error)/2
    tan_angle = dnp.tan(dnp.radians(2*fitted_c1_forcam - d1_error))
    
    fit_cam_opt = dnp.fit.fit(func_cam, cam, tan_angle, [0,0],[(-30,30),(-100,100)], optimizer='global')
    h_cam_error = 250 + fit_cam_opt[0]
    z_cam = 3200 + fit_cam_opt[1]
    fitted_cam = (z_cam * dnp.tan(dnp.radians(2*fitted_c1_forcam - d1_error))) - h_cam_error
    
    fit_lambda_opt = dnp.fit.fit(func_lambda, fitted_c1_forcam - d1_error/2, wavelength, [0,0], [(0.3,0.32),(0,0.03)], optimizer='global')
    fitted_d0 = fit_lambda_opt[0]
    lam_error = fit_lambda_opt[1]
    fit_wavelength = 2*fitted_d0*dnp.sin(dnp.radians(fitted_c1_forcam - d1_error/2))+lam_error
    
    #You would think it obvious, but I could not figure out how to get dnp.fit.fit to work with one bounded parameter, hence the 2nd 'dummy' parameter.
    fit_theta2_opt = dnp.fit.fit(func_theta2, c2, theta_theory, [0,0], [(-1,1),(0,0.0000000001)], optimizer='global')
    c2_error = fit_theta2_opt[0]
    fitted_bragg2 = c2 - c2_error
    
    print ""
    print "Displaying quality of fits performed when calculating model parameters (R-squared values): "
    print "    Fit of crystal 1 rotation = ", R2(c1, fitted_c1_forcam) 
    print "    Fit of crystal 2 rotation = ", R2(theta_theory, fitted_bragg2) 
    print "    Fit of camera position   = ", R2(cam, fitted_cam)
    print "    Fit of energy            = ", R2(wavelength, fit_wavelength)    
    
    range_target_c1 = dnp.zeros(num)
    range_target_c2 = dnp.zeros(num)
    range_target_z = dnp.zeros(num)
    range_target_cam = dnp.zeros(num)
    co = -1
    for k in wavelength:
        co = co + 1
        mo = calc_motor(k, lam_error, fitted_d0, d1_error, d_spacing, c2_error, 50, z_error_forcam, z_cam, h_cam_error)
        range_target_c1[co] = mo[0,0]
        range_target_c2[co] = mo[1,0]
        range_target_z[co] = mo[2,0]
        range_target_cam[co] = mo[3,0]
        
    print ""
    print "Displaying quality of fits when calculating motor positions as a function of energy (R-squared values): "
    print "    Fit of crystal 1 rotation = ", R2(c1, -range_target_c1) 
    print "    Fit of crystal 2 rotation = ", R2(c2, -range_target_c2)
    print "    Fit of z translation     = ", R2(z, range_target_z)
    print "    Fit of camera position   = ", R2(cam, range_target_cam)
    
    motor = calc_motor(target_wavelength, lam_error, fitted_d0, d1_error, d_spacing, c2_error, 50, z_error_forcam, z_cam, h_cam_error)
    
    target_c1, target_c2, target_z, target_cam = motor
    #target_c1, target_c2, target_z, target_cam = calc_motor(target_wavelength, lam_error, fitted_d0, d1_error, d_spacing, c2_error, 50, z_error_forcam, z_cam, h_cam_error)
    
#    print "WARNING: Old calibration data used, so crude offsets are applied to output motor positions: Crystal 1, -38; Crystal 2, -18; z, -4.5, Camera position, +18.5."
#    print "         Crystal and camera positions will still require adjustment and the energy should still be measured if accuracy is required."
    
    crystal1 = 1000*target_c1[0,0]# - 38
    crystal2 = 1000*target_c2[0,0]# - 18
    translation = target_z[0,0] # - 4.5
    cam = target_cam[0,0]# + 18.5
        
    print ""
    print "Displaying calculated motor positions for desired energy of", target_energy, " keV (", 10*wavelength , " Angstrom):"
    print "    Crystal 1                = ", crystal1
    print "    Crystal 2                = ", crystal2
    print "    z translation            = ", translation
    print "    Camera position          = ", cam
    print ""
    print "N.B. Only 3 calibration data points. Calibration unreliable. Use at your own risk! Definitely do not use above 90 keV."
    
    print ""
    print "Moving motors to calculated motor positions"
    pos(mc1_bragg, crystal1)
    pos(mc2_bragg, crystal2)
    pos(mc2_z, translation)
    pos(camMono2_y, cam)
    print ""
    print "Monochromator at nominally ", target_energy, "keV. Manual adjustment likely to be required."

print "finished loading 'moveToBeamEnergy' "
