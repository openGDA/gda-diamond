'''
XAS energy scan supports either fast energy scan , slow energy scan or both enabled by parameters

@since: 20 June 2022
@contact: Fajin Yuan
@group: Diamond I21 Team
@status: tested in dummy mode  

Created on 12th Oct 2021

@author: i21user
'''

from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
import installation
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]

##########################################
#### define Sample positions for (pi, 0)
##########################################
x_sample_pi0 = -1.815
y_sample_pi0 = -0.27
z_sample_pi0 = +2.297

phi_sample_pi0 = -8.0
chi_sample_pi0 = +10.85    
    
#############################################
# User Section - defining exit slit opening
#############################################
exit_slit = 30

###########################################################################
## Define Polarisation value - valid value is (LH,LV,CR,CL,LH3,LV3,LH5,LV5)
###########################################################################
pol_list = [LH, LV]

#########################################################################
## Define energy range and step in eV, counting time in secs
#########################################################################
E_initial = 520.0
E_final = 550.0
E_step = 0.05

fast_scan_counting_time = 0.1  #do not use a counting time less than 0.1 secs
slow_scan_counting_time =1

########################################################
#### define NORMAL INCIDENCE , THETA = 90 ##############
########################################################
th_normal = 90

########################################################
#### define  GRAZING IN , THETA = 20 ###################
########################################################
th_grazing = 20

########################################################
#### define scan method to use
########################################################
use_fast_scan = False
use_slow_scan =True

########################################################################
## Define amplifier's gain
#########################################################################
# to change Femto Gain if the diode signal or drain current is too small or is saturating
# value must be one of (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9) for "Low Noise" mode,  
if installation.isLive(): #only live mode requires this - i.e running in i21 GDA.
    from gdaserver import draincurrent_i, diff1_i,fy2_i # @UnresolvedImport
    draincurrent_i.setGain(1e9)
    diff1_i.setGain(1e8)
    fy2_i.setGain(1e8)
# please do NOT change m4c1 gain !!!

######################################################################
## define collection order in each axis - must match with each other
######################################################################

th_collection_order =  [th_normal, th_normal, th_grazing, th_grazing]
pol_collection_order = [LH,        LV,        LH,         LV        ]

#create tuple
collection_orders = zip(th_collection_order, pol_collection_order)
print("Data collections are order in list of (th, pol): %r" % collection_orders)

########################################################################
#########  define fast XAS scan function (on the fly) ##################
########################################################################
def fast_energy_scan_collection(thval, polval):
    from scannabledevices.checkbeanscannables import checkbeamcv
    from gdaserver import th # @UnresolvedImport
    from scannable.continuous.continuous_energy_scannables import draincurrent_c, diff1_c, fy2_c, m4c1_c, energy
    from scan.cvscan import cvscan
    from functions.go_founctions import go
    
    print("move th to %f ..." % thval)
    th.asynchronousMoveTo(thval)
    # # Change polarisation to pol
    go(E_initial, polval)
    th.waitWhileBusy()
    cvscan(energy, E_initial, E_final, E_step,  draincurrent_c, fast_scan_counting_time,  diff1_c, fast_scan_counting_time,  fy2_c, fast_scan_counting_time,  m4c1_c, fast_scan_counting_time, checkbeamcv)

########################################################################
#########  define slow XAS scan function (step mode)  ##################
########################################################################
def slow_energy_scan_collection(thval, polval):
    from scannabledevices.checkbeanscannables import checkbeam
    from gdaserver import th, m4c1 # @UnresolvedImport
    from scannable.continuous.continuous_energy_scannables import energy
    from gdascripts.scan.installStandardScansWithProcessing import scan
    from functions.go_founctions import go
    
    print("move th to %f ..." % thval)
    th.asynchronousMoveTo(thval)
    # # # Change polarisation to polval
    go(E_initial, polval)
    th.waitWhileBusy()
    scan(energy, E_initial, E_final, E_step, draincurrent_i, slow_scan_counting_time,  diff1_i, slow_scan_counting_time, fy2_i, slow_scan_counting_time,  m4c1, slow_scan_counting_time, checkbeam)
     
answer = "y"

# you can comment out the following line to remove user input required when running this script
answer = raw_input("\nAre these collection parameters correct to continue [y/n]?")

#########################################################
#########  Data Collection ################
#########################################################
if answer == "y":
    from gdaserver import xyz_stage, s5v1gap, difftth, m5tth, fastshutter, gv17 # @UnresolvedImport
    from shutters.detectorShutterControl import erio, primary
    
    #move to sample position
    print("move sampel stage to %r ..." % [x_sample_pi0, y_sample_pi0, z_sample_pi0])
    xyz_stage.asynchronousMoveTo([x_sample_pi0, y_sample_pi0, z_sample_pi0])
    
    # defining exit slit opening
    print("move s5v1gap to %f ..." % exit_slit)
    s5v1gap.asynchronousMoveTo(exit_slit)
    
    # Position photo diode to so that we measure XAS through M5 optics
    difftth_val = float(m5tth.getPosition())+1.5
    print("move difftth to %f ..." % difftth_val)
    difftth.asynchronousMoveTo(difftth_val)
    
    s5v1gap.waitWhileBusy()
    difftth.waitWhileBusy()
    xyz_stage.waitWhileBusy()
    print("All motions are now completed")
    
    # Keep Fast Shutter open throughout XAS measurements
    erio();fastshutter('Open');gv17('Close')
    
    if use_fast_scan:
        for th_val, pol_val in collection_orders:
            fast_energy_scan_collection(th_val, pol_val)

    if use_slow_scan:
        for th_val, pol_val in collection_orders:
            slow_energy_scan_collection(th_val, pol_val)
    
    
    # ###################################################################
    # # Revert fast shutter to normal RIXS operation
    primary();fastshutter('Open');gv17('Open')
      
    # # Position diff1 so that it is out of the way of the outgoing x-ray beam
    difftth.moveTo(0)
  
print('All of the macro is completed !!!')


