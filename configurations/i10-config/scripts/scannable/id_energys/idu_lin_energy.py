from Diamond.energyScannableLinearArbitrary import EnergyScannableLinearArbitrary, PolarisationAngleScannable

# Linear arbitrary polarisation for idu up to 1000 eV

from Diamond.Poly import Poly
from gdaserver import idu_gap, idu_rowphase1, idu_rowphase2, idu_rowphase3,\
    idu_rowphase4, idu_jawphase, pgm_energy
from utils.ExceptionLogs import localStation_exception
import sys
from lookups.cvs2dictionary import loadCVSTable
from scannable.id_energys.lookupTableDirectory import lookup_tables_dir
from scannable.continuous.deprecated.FollowerScannable import SilentFollowerScannable

print "-"*100

try:
    print "Creating idu energy and energy follower scannables for Linear Arbitrary polarisation mode:"
    print "    'idu_lin_arbitrary_energy', 'idu_lin_arbitrary_energy_follower', 'idu_lin_arbitrary_angle' - IDD Linear Arbitrary polarisation energy and follower, and angle"
    idu_lin_arbitrary_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_arbitrary_energy.csv"))
    idu_lin_arbitrary_energy = EnergyScannableLinearArbitrary('idu_lin_arbitrary_energy',
        idu_gap, idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, 
        idu_jawphase, pgm_energy, 'idu_lin_arbitrary_angle',
        angle_min_Deg=0., angle_max_Deg=180., angle_threshold_Deg=30., 
        energy_min_eV=612.2, energy_max_eV=1001.0,  
        rowphase1_from_energy=dict(zip(idu_lin_arbitrary_table['energy'], idu_lin_arbitrary_table['rowphase1'])),
        rowphase2_from_energy=0.,
        rowphase3_from_energy=dict(zip(idu_lin_arbitrary_table['energy'], idu_lin_arbitrary_table['rowphase3'])),
        rowphase4_from_energy=0., 
        gap_from_energy=dict(zip(idu_lin_arbitrary_table['energy'], idu_lin_arbitrary_table['idgap'])),
        #jawphase = ( alpha_real - 120. ) / 7.5
        jawphase_from_angle=Poly([-120./7.5, 1./7.5], power0first=True))
    idu_lin_arbitrary_energy_maximum=max(idu_lin_arbitrary_table['energy'])
    idu_lin_arbitrary_energy_minimum=min(idu_lin_arbitrary_table['energy'])
    idu_lin_arbitrary_energy_follower = SilentFollowerScannable('idu_circ_pos_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_arbitrary_energy, follower_tolerance=0.35)
    idu_lin_arbitrary_energy.concurrentRowphaseMoves=True
    idu_lin_arbitrary_energy.energyMode=True
     
    idu_lin_arbitrary_angle = PolarisationAngleScannable('idu_lin_arbitrary_angle', idu_lin_arbitrary_energy)
except:
    localStation_exception(sys.exc_info(), "initialising idu linear arbitrary energy followers")
    
print "==== idu Linear Arbitrary energy scannable done.==== "