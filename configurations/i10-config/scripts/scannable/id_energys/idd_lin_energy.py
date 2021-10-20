from Diamond.energyScannableLinearArbitrary import EnergyScannableLinearArbitrary, PolarisationAngleScannable

# Linear arbitrary polarisation for idd up to 1000 eV

from Diamond.Poly import Poly
from gdaserver import idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3,\
    idd_rowphase4, idd_jawphase, pgm_energy
from utils.ExceptionLogs import localStation_exception
import sys
from lookups.cvs2dictionary import loadCVSTable
from scannable.id_energys.lookupTableDirectory import lookup_tables_dir
from scannable.continuous.deprecated.FollowerScannable import SilentFollowerScannable

print "-"*100

try:
    print "Creating idd energy and energy follower scannables for Linear Arbitrary polarisation mode:"
    print "    'idd_lin_arbitrary_energy', 'idd_lin_arbitrary_energy_follower', 'idd_lin_arbitrary_angle' - IDD Linear Arbitrary polarisation energy and follower, and angle"
    idd_lin_arbitrary_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idd_lin_arbitrary_energy.csv"))
    idd_lin_arbitrary_energy = EnergyScannableLinearArbitrary('idd_lin_arbitrary_energy',
        idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, 
        idd_jawphase, pgm_energy, 'idd_lin_arbitrary_angle',
        angle_min_Deg=0., angle_max_Deg=180., angle_threshold_Deg=30., 
        energy_min_eV=612.2, energy_max_eV=1001.0,  
        rowphase1_from_energy=dict(zip(idd_lin_arbitrary_table['energy'], idd_lin_arbitrary_table['rowphase1'])),
        rowphase2_from_energy=0.,
        rowphase3_from_energy=dict(zip(idd_lin_arbitrary_table['energy'], idd_lin_arbitrary_table['rowphase3'])),
        rowphase4_from_energy=0., 
        gap_from_energy=dict(zip(idd_lin_arbitrary_table['energy'], idd_lin_arbitrary_table['idgap'])),
        #jawphase = ( alpha_real - 120. ) / 7.5
        jawphase_from_angle=Poly([-120./7.5, 1./7.5], power0first=True))
    idd_lin_arbitrary_energy_maximum=max(idd_lin_arbitrary_table['energy'])
    idd_lin_arbitrary_energy_minimum=min(idd_lin_arbitrary_table['energy'])
    idd_lin_arbitrary_energy_follower = SilentFollowerScannable('idd_circ_pos_energy_follower', followed_scannable=pgm_energy, follower_scannable=idd_lin_arbitrary_energy, follower_tolerance=0.35)
    idd_lin_arbitrary_energy.concurrentRowphaseMoves=True
    idd_lin_arbitrary_energy.energyMode=True
     
    idd_lin_arbitrary_angle = PolarisationAngleScannable('idd_lin_arbitrary_angle', idd_lin_arbitrary_energy)
except:
    localStation_exception(sys.exc_info(), "initialising idd linear arbitrary energy followers")
    
print "==== idd Linear Arbitrary energy scannable done.==== "