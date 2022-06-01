'''
Created on 12th Oct 2021

@author: SA
'''

import math as mh
from gdaserver import x,y,z,th,phi,chi, s5v1gap, energy, andor, difftth, fastshutter, spech, m4c1, checkbeam  # @UnresolvedImport
from acquisition.darkImageAcqusition import acquire_dark_image
from shutters.detectorShutterControl import primary
from functions.go_founctions import go
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
from gda.jython.commands.ScannableCommands import inc
from acquisition.acquireCarbonTapeImages import acquire_ctape_image
from acquisition.acquire_images import acquireRIXS
from gdascripts.utils import frange

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]
#########################################################################


#########################################################################
# definition of the sample and ctape position along (pi,0)
#########################################################################

x_sample_pi0=-1.357
y_sample_pi0=-1.5
z_sample_pi0=-0.9
th_sample_pi0 = 138.16
phi_sample_pi0 = -50.7
chi_sample_pi0 = 3.3

x_ctape_pi0=+0.39
y_ctape_pi0=-1.5
z_ctape_pi0=-3.5
th_ctape_pi0 = 138.16
phi_ctape_pi0 = -50.7
chi_ctape_pi0 = 3.3

def sample_pi0():
    '''move to sample_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_sample_pi0)
    y.asynchronousMovTo(y_sample_pi0)
    z.asynchronousMovTo(z_sample_pi0)
    th.asynchronousMovTo(th_sample_pi0)
    phi.asynchronousMovTo(phi_sample_pi0)
    chi.asynchronousMovTo(chi_sample_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
   

def ctape_pi0():
    '''move to ctape_pi0 position concurrently and wait until all moves complete
    '''
    x.asynchronousMovTo(x_ctape_pi0)
    y.asynchronousMovTo(y_ctape_pi0)
    z.asynchronousMovTo(z_ctape_pi0)
    th.asynchronousMovTo(th_ctape_pi0)
    phi.asynchronousMovTo(phi_ctape_pi0)
    chi.asynchronousMovTo(chi_ctape_pi0)
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()



#####################################
# defining exit slit opening
#####################################
s5v1gap.moveTo(40)

#####################################
# Information for spech calculation
#####################################
specgammaval = 30 #Needs to be updated if gamma is changed.
Detector_pxsz = 0.01358
E_dispersion = 0.00801  #needs to be updated to the current experimental value
energy_val_fix=529.5  #Resonant energy
spech_val_fix=1386.53  #Spech corresponding to the resonant energy

#####################################
#Defining CCD parameters
#####################################

sample_no_images = 1
ctape_no_images = 1

sample_exposure_time = 20
ctape_exposure_time = 5

##################################################################
#We acquire some dark images before the E scan:
##################################################################
#Dark Image
energy.moveTo(500)
acquire_dark_image(1, andor, sample_exposure_time)


######################################
# moving diode to 0
######################################
difftth.moveTo(0)

#################################################################
###################### ACQUIRING DATA ###########################
#################################################################
primary()
fastshutter('Open')

th.moveTo(45)
en_val = 529.75

# change polarization to LV
go(en_val, LV)

#############################################################
###################### Survey Scans #########################
#############################################################

for j in range(15):
    energy.moveTo(en_val)
    spech_val = spech_val_fix+(energy_val_fix-en_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
    spech.moveTo(spech_val)
    
    ctape_pi0()
    acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
    
    sample_pi0()    ##these are not efficient moves
    inc(z, 0.01*j)
    print('RIXS at Energy = %.2f, and spech=%.2f'%(en_val,spech_val))
    acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
    print(j+1)
         

#############################################################
######################## Energy map #########################
#############################################################

en_list = frange(526,536.01,0.25)
 

for j,en_val in enumerate(en_list):
    energy.moveTo(en_val)
    spech_val = spech_val_fix+(energy_val_fix-en_val)*Detector_pxsz*mh.sin(specgammaval*mh.pi/180)/E_dispersion
    spech.moveTo(spech_val)  
          
    print('RIXS at Energy = %.2f, and spech=%.2f'%(en_val,spech_val))
    for i in range(10):
        ctape_pi0()
        acquire_ctape_image(ctape_no_images, andor, ctape_exposure_time, m4c1, ctape_exposure_time, checkbeam)
        sample_pi0()
        inc(z, 0.01*j)
        inc(y, 0.05*i)
        acquireRIXS(sample_no_images, andor, sample_exposure_time, m4c1, sample_exposure_time, checkbeam)
    print(j+1)
        

#################################################
#################################################

# move spech to the optimised position for qscan (resonance)

energy.moveTo(energy_val_fix)
spech.moveTo(spech_val_fix) 

# feabsorber('Close')

#####################################################################
print('Macro is completed !!!')