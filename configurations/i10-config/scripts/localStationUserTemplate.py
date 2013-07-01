###############################################################################
# This script will be run at the end of the main i10 localStation script.     #
#                                                                             #
# Thus it will be run whenever the `reset_namespace` command is run on the    #
# Jython terminal console in GDA, or the gda servers are restarted.           #
#                                                                             #
# CAUTION: Anyone may edit this script.                                       #
#                                                                             #
#          Things you put in here late at night may affect future user runs.  #
#                                                                             #
###############################################################################
print "Running /dls/i10/scripts/localStationUser.py (user editable)"

#######################################+#######################################
###                             Energy scannables                           ###
###############################################################################
#                                                                             #
### Comment out the energy scannables which you don't wish to use.            #
#                                                                             #
###############################################################################

### Standard energy scannables

run("0_IMPORTANT/id_energy_dec12.py")
 
#run("./Archive/idd_energy.py")
#run("./Archive/idd_lin_energy.py")

### Special purpose energy scannables

#run("./Archive/idd_energy_march12.py")
#run("./Archive/idd_energy_0322.py")

### Visit specific energy scannables

#run("./si7726/idd_energy_july12.py")
#run("./si7670/idd_energy_july12.py")

#######################################+#######################################
###                             POMS scannables                             ###
###############################################################################
#                                                                             #
### Comment out POMS scannables when not in use.                              #
#                                                                             #
###############################################################################
from poms.localStationPoms import *

vmag = poms_default_vmag('vmag')
print repr(vmag)

###############################################################################
# Select which Flipper(s) you want to use
###############################################################################
### Configure vflipper using defaults

print repr(poms_default_vflipper('vflipper'))
#vflipper= poms_default_vflipper('vflipper')
#print repr(vflipper)

### Configure vflipper manually
from poms.PomsVflipper import FlipperDeviceClass

#vflipper = FlipperDeviceClass('vflipper', nameMagnet='vmag',
#    nameCounterTimerA='mac116',
#    nameCounterTimerB='mac117', nameCounterTimerC='mac118');

#vflipper = FlipperDeviceClass('vflipper', nameMagnet='vmag',
#    nameCounterTimerA='mac116',
#    nameCounterTimerB='mac120', nameCounterTimerC='mac122');

vflipper = FlipperDeviceClass('vflipper', nameMagnet='vmag',
    nameCounterTimerA='macr19',
    nameCounterTimerB='macr16', nameCounterTimerC='mac117'); # 20130618

###############################################################################
### Configure vflipperCalc using defaults

print      repr(poms_default_vflipper_calc('vflipperCalc'))
#vflipperCalc = poms_default_vflipper_calc('vflipperCalc')
#print repr(vflipperCalc)

### Configure vflipperCalc manually
from poms.PomsVflipperCalc import FlipperCalcDeviceClass

#vflipperCalc = FlipperCalcDeviceClass('vflipperCalc', nameMagnet='vmag',
#        nameCounterTimerA='macr19',
#        nameCounterTimerB='macr16', nameCounterTimerC='mac117',
#        nameCounterTimerD='macj118', nameCounterTimerE='mac11',
#        nameCalc1='EDIF', calc1='B2/A2-B1/A1',
#        nameCalc2='X2',   calc2='B2/A2+B1/A1',
#        nameCalc3='EXAS', calc3='X2/2.0',
#        nameCalc4='TDIF', calc4='C1/A1-C2/A2',
#        nameCalc5='X5',   calc5='C1/A1+C2/A2',
#        nameCalc6='TXAS', calc6='X5/2.0')
#Note: For some reason the expression evaluation doesn't work with parentheses
#      at the moment, so you will have to rely on operator precedence and use
#      of output values as intermediate values as in the example above

vflipperCalc = FlipperCalcDeviceClass('vflipperCalc', nameMagnet='vmag',
        nameCounterTimerA='macr19',
        nameCounterTimerB='macr16', nameCounterTimerC='mac117',
        nameCounterTimerD='macj118', nameCounterTimerE='mac11',
        nameCalc1='EDIF', calc1='B2/A2-B1/A1',
        nameCalc2='X2',   calc2='B2/A2+B1/A1',
        nameCalc3='EXAS', calc3='X2/2.0',
        nameCalc4='TDIF', calc4='C1/A1-C2/A2',
        nameCalc5='X5',   calc5='C1/A1+C2/A2',
        nameCalc6='TXAS', calc6='X5/2.0')

###############################################################################
### Configure vflipperRaw using defaults

#print     repr(poms_default_vflipper_raw('vflipperRaw'))
#vflipperRaw = poms_default_vflipper_raw('vflipperRaw')
#print repr(vflipperRaw)

### Configure vflipperRaw manually
#from poms.PomsVflipperRaw import FlipperRawDeviceClass

#vflipperRaw = FlipperRawDeviceClass('vflipperRaw', nameMagnet='vmag',
#    nameCounterTimerA='mac116', nameCounterTimerB='mac120',
#    nameCounterTimerC='mac121', nameCounterTimerD='mac122',
#    nameCounterTimerE='mac123');

#vflipperRaw = FlipperRawDeviceClass('vflipperRaw', nameMagnet='vmag',
#    nameCounterTimerA='macr1',  nameCounterTimerB='macr10',
#    nameCounterTimerC='macr11', nameCounterTimerD='macr31',
#    nameCounterTimerE='macr23'); # 20130618

#######################################+#######################################
###                      Colby Delay Line scannables                        ###
###############################################################################
#                                                                             #
### Comment out this scannable if you don't wish to it.                       #
#                                                                             #
###############################################################################

from other_devices.colby_delay_line import DelayLineClass

# Delay line on SER2
#delay=DelayLineClass('delay', 'BL10I-EA-USER-01:SER2.AOUT',
#    'BL10I-EA-USER-01:SER2.TINP', "BL10I-EA-USER-01:SER2.IEOS",
#    '%', '%.15f', 'Colby PDL-100A Programmable Delay Line')

# Delay line on SER3
delay=DelayLineClass('delay', 'BL10I-EA-USER-01:SER3.AOUT',
    'BL10I-EA-USER-01:SER3.TINP', 'BL10I-EA-USER-01:SER3.IEOS',
    '%', '%.15f', 'Colby PDL-100A Programmable Delay Line')

print 'On BLADE Synoptic, select UI1, then Serial Ch 3, then make'
print "sure that both input and output terminators are \\r\\n"

#######################################+#######################################
###                    Polarisation Analyser scannables                     ###
###############################################################################
#                                                                             #
### Comment out any polarisation scannables which you don't wish to use.      #
#                                                                             #
###############################################################################

### Standard polarisation scannables

#run("./0_IMPORTANT/paSetup.py")

### Special purpose polarisation scannables

#run("./paSetup_co.py")

### Visit specific polarisation scannables

#run("./Leeds/paSetup_co.py")
#run("./usermacros/durham/paSetup.py")
#run("./si7701_1/paSetup_co.py")
#run("./si7701-2/paSetup_fe.py")

#######################################+#######################################
###                        Lakeshore 340 scannables                         ###
###############################################################################
#                                                                             #
# Note: If the lakeshore serial interface is plugged into the user patch      #
#       panel then set lakeshore_by_patch_panel to True.                      #
#                                                                             #
#       If the lakeshore serial interface is plugged into the IOC in the      #
#       RASOR rack then set lakeshore_by_patch_panel to False.                #
#                                                                             #
###############################################################################

#lakeshore_by_patch_panel=True
#lakeshore_by_patch_panel=False

#-----------------------------------------------------------------------------#
#if lakeshore_by_patch_panel:
#    run("./0_IMPORTANT/Lakeshore_340_I10.py")
#    add_default ls_340_getA
#    add_default ls_340_getB
#else:
#    add_default lakeshore

#######################################+#######################################
###                     Other scripts and configuration                     ###
###############################################################################
#                                                                             #
###############################################################################

### Standard options


### Special purpose options


### Visit specific options


#add_default macj117
#add_default macj118
#add_default ips_field
#add_default itc2
#add_default magj1yins
#add_default magj1yrot
#add_default m6_pitch

add_default macr16
add_default macr17
add_default macr18
add_default macr19
add_default m4_pitch
add_default m4_yaw
add_default user1_axis6
add_default mac117
add_default macj117
add_default macj118

#itc2.temp_tolerance=0.1
#itc2.stable_time_sec=300

#add_default ui1ai1

run("0_IMPORTANT/macNorm.py")
#add_default drain
#add_default fluo

### Loading math for tuple definition of non-equidistant E scanning
import scisoftpy as dnp

#add_default macNormr16
#add_default macNorm118

#######################################+#######################################
###                                   END                                   ###
###############################################################################
print "Completed running /dls/i10/scripts/localStationUser.py (user editable)"
