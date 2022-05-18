'''
Created on 27th Mar 2019

@author: i21user

modified on 17/IX/19 by MGF
modified on 18/iX/19 by KJZ 
modified on 10/09/21 by JC 

'''
import math as mh
from gdaserver import x,y,z,th,phi,chi, s5v1gap, energy, andor, difftth, m4c1, checkbeam  # @UnresolvedImport
from gdascripts.utils import frange
from acquisition.darkImageAcqusition import acquire_dark_image
from shutters.detectorShutterControl import primary
from functions.go_founctions import go
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from templates.momentumTransferFunctions import qtransinplane2th
from gdascripts.metadata.nexus_metadata_class import meta
from templates.unitTransferFunctions import energy2wavelength, dspacing
from acquisition.acquireCarbonTapeImages import acquire_ctape_image
from acquisition.acquireImages import acquireRIXS
LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]


################################################################
######## Defining the spectrometer tth scattering angle
################################################################

tth = 150.0
tth_m5hq = tth + 4.0
tth_m5lq = tth - 4.0


########################################################################
##################### SAMPLE PARAMETERS ################################
########################################################################

###########################################################
# Lattice parameters
###########################################################

a = 3.88
b = 3.82
c = 11.68


########################################################################
# definition of the sample and ctape position along (pi,0)
########################################################################

x_sample_pi0= +0.4429
y_sample_pi0= +0.7
z_sample_pi0= +1.6
phi_sample_pi0= 0
 
 
x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5
phi_ctape_pi0= 0
 
 
chi_offset_pi0 = 0.0
th_offset_pi0 = +2.8+2.393
 
def sample_pi0():
    '''move to sample_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_sample_pi0)
    y.asynchronousMovTo(y_sample_pi0)
    z.asynchronousMovTo(z_sample_pi0)
    phi.asynchronousMovTo(phi_sample_pi0)
    chi.asynchronousMovTo(chi_offset_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
     
     
def ctape_pi0():
    '''move to ctape_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_ctape_pi0)
    y.asynchronousMovTo(y_ctape_pi0)
    z.asynchronousMovTo(z_ctape_pi0)
    phi.asynchronousMovTo(phi_ctape_pi0)
    chi.asynchronousMovTo(chi_offset_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
     


#################################################################
# definition of the sample and ctape position along (pi,pi)
#################################################################

x_sample_pipi=-1.373
y_sample_pipi=-2.0
z_sample_pipi=+0.9
phi_sample_pipi= 45
 
x_ctape_pipi=+0.18
y_ctape_pipi=-2.0
z_ctape_pipi=-2.8
phi_ctape_pipi= 45
 

chi_offset_pipi = 0.0
th_offset_pipi = +2.8+2.393
 
def sample_pipi():
    '''move to sample_pipi position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_sample_pipi)
    y.asynchronousMovTo(y_sample_pipi)
    z.asynchronousMovTo(z_sample_pipi)
    phi.asynchronousMovTo(phi_sample_pipi)
    chi.asynchronousMovTo(chi_offset_pipi)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
     
 
def ctape_pipi():
    '''move to ctape_pipi position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_ctape_pipi)
    y.asynchronousMovTo(y_ctape_pipi)
    z.asynchronousMovTo(z_ctape_pipi)
    phi.asynchronousMovTo(phi_ctape_pipi)
    chi.asynchronousMovTo(chi_offset_pipi)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
     

    
##############################################################
#####################################
# defining exit slit opening
#####################################
exit_slit = 20
s5v1gap.moveTo(exit_slit)
#####################################

######################################
# moving diode to 0
######################################
difftth.moveTo(0)

##############################################################
#Defining Energy
##############################################################
E_initial = 931.5


########################################################################
#Defining CCD parameters
########################################################################

sample_no_images = 2
ctape_no_images = 1

sample_exposure_time = 30
ctape_exposure_time = 30


#####################################################################
################# Q range and steps #################################
#####################################################################

#### (PI, 0)

qStart_pi0 = 0.3
qEnd_pi0 = 0.5
qStep_pi0 = 0.05
n_points_pi0 = int((qEnd_pi0-qStart_pi0)/qStep_pi0 + 1)

qlist_pi0 = frange(qStart_pi0, qEnd_pi0, qStep_pi0)

#### (PI, PI)

qStart_pipi = 0.3
qEnd_pipi = 0.6
qStep_pipi = 0.05
n_points_pipi = int((qEnd_pipi-qStart_pipi)/qStep_pipi + 1)

qlist_pipi = frange(qStart_pipi, qEnd_pipi, qStep_pipi)



############################################################
################# ACQUIRING DATA ###########################


##################################################################
#We acquire some dark images before the scan:
##################################################################
#Dark Image
energy.moveTo(931.5)
acquire_dark_image(1, andor, sample_exposure_time)

###########################################

#################### HQ MIRROR ###########################
primary()

#############################################################
###################### SAMPLE (PI,0)########################
#############################################################
def collect_pi0_data():
    for i, qval in enumerate(qlist_pi0):
        thval = qtransinplane2th(E_initial,qval,th_offset_pi0,tth_m5hq,1.,0.,0., a, b, c) 
        th.moveTo(thval)
        meta.addScalar("Q", "H", qval) 
        
        print('Total number of points is %d. Point number %d is at qtrans_inplane=%.4f, th=%.3f for ctape(pi0)'%(len(qlist_pi0),i+1.0,qval,thval))
        ctape_pi0()
        acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    
        print('Total number of points is %d. Point number %d is at qtrans_inplane=%.4f, th=%.3f for sample(pi0)'%(len(qlist_pi0),i+1.0,qval,thval))
        sample_pi0()
        acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)    
        print('*******************************************************************')
        
        meta.rm("Q", "H")

##########################################
################### LV ################

go(E_initial, LV)
energy.moveTo(E_initial)
print('scan between q= %.4f and q= %.4f using the M5hq mirror, s5v1gap = %d, LV, energy = %.2f'%(qStart_pi0,qEnd_pi0, exit_slit, E_initial))
collect_pi0_data()

##########################################
################### LH ################

go(E_initial, LH)
energy.moveTo(E_initial)
print('scan between q= %.4f and q= %.4f using the M5hq mirror, s5v1gap = %d, LH, energy = %.2f'%(qStart_pi0,qEnd_pi0, exit_slit, E_initial))
collect_pi0_data()


#############################################################
###################### SAMPLE (PI,PI)########################
#############################################################
def collect_pipi_data():
    for i, qval in enumerate(qlist_pipi):
        thval = qtransinplane2th(E_initial,qval,th_offset_pipi,tth_m5hq,1.,1.,0., a, b, c) 
        th.moveTo(thval)
        meta.addScalar("Q", "H", qval) 
        
        print('Total number of points is %d. Point number %d is at qtrans_inplane=%.4f, th=%.3f for ctape(pipi)'%(len(qlist_pipi),i+1.0,qval,thval))
        ctape_pipi()
        acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    
        print('Total number of points is %d. Point number %d is at qtrans_inplane=%.4f, th=%.3f for sample(pipi)'%(len(qlist_pipi),i+1.0,qval,thval))
        sample_pipi()
        acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)    
        print('*******************************************************************')

        meta.rm("Q", "H")

#######################################
################### LV ################

go(E_initial, LV)
energy.moveTo(E_initial)
print('scan between q= %.4f and q= %.4f using the M5hq mirror, s5v1gap = %d, LV, energy = %.2f'%(qStart_pipi,qEnd_pipi, exit_slit, E_initial))
collect_pipi_data()


#######################################
################### LH ################

go(E_initial, LH)
energy.moveTo(E_initial)
print('scan between q= %.4f and q= %.4f using the M5hq mirror, s5v1gap = %d, LH, energy = %.2f'%(qStart_pipi,qEnd_pipi, exit_slit, E_initial))
collect_pipi_data()

    
##########################################

#####################################################################
print('Macro is completed !!!')