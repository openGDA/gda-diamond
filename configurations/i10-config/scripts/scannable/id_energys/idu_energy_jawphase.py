'''
Create IDU energy scannables for different polarisation using ID jawphase for cvscan and ID tracking
'''
from gdaserver import idu_gap, idu_rowphase1, idu_jawphase, idu_rowphase2,\
    idu_rowphase3, idu_rowphase4, pgm_energy
from lookups.cvs2dictionary import loadCVSTable
from scannable.id_energys.lookupTableDirectory import lookup_tables_dir
from utils.ExceptionLogs import localStation_exception
import sys

print "-"*100

try:
    from Diamond.energyScannableLookup import EnergyScannableLookup
    from scannable.continuous.deprecated.FollowerScannable import SilentFollowerScannable
    
    print "Creating idu jaw energy and jaw energy follower scannables for different polarisation modes:"
    print "    'idu_lin_hor_jaw_energy','idu_lin_hor_jaw_energy_follower' - IDU Linear Horizontal polarisation jawphase energy and follower"
    idu_lin_hor_jaw_table =loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_hor_energy2jawphase.csv"))
    idu_lin_hor_jaw_energy = EnergyScannableLookup('idu_lin_hor_jaw_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0,
            jawphase_lookup=dict(zip(idu_lin_hor_jaw_table['energy'], idu_lin_hor_jaw_table['jawphase']))
            )
    idu_lin_hor_jaw_energy_maximum=max(idu_lin_hor_jaw_table['energy'])
    idu_lin_hor_jaw_energy_minimum=min(idu_lin_hor_jaw_table['energy'])
    idu_lin_hor_jaw_energy_follower = SilentFollowerScannable('idu_lin_hor_jaw_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_hor_jaw_energy, follower_tolerance=0.35)
    idu_lin_hor_jaw_energy.concurrentRowphaseMoves=True
    idu_lin_hor_jaw_energy.energyMode=False #using jaw pahase (default)

    print "    'idu_lin_ver_jaw_energy', 'idu_lin_ver_jaw_energy_follower' - IDU Linear Vertical polarisation jawphase energy and follower"
    idu_lin_ver_jaw_table =loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_ver_energy2jawphase.csv"))
    idu_lin_ver_jaw_energy = EnergyScannableLookup('idu_lin_ver_jaw_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=16, rowphase1=24, rowphase2=0, rowphase3=24, rowphase4=0,
            jawphase_lookup=dict(zip(idu_lin_ver_jaw_table['energy'], idu_lin_ver_jaw_table['jawphase']))
            )
    idu_lin_ver_jaw_energy_maximum=max(idu_lin_ver_jaw_table['energy'])
    idu_lin_ver_jaw_energy_minimum=min(idu_lin_ver_jaw_table['energy'])
    idu_lin_ver_jaw_energy_follower = SilentFollowerScannable('idu_lin_ver_jaw_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_ver_jaw_energy, follower_tolerance=0.35)
    idu_lin_ver_jaw_energy.concurrentRowphaseMoves=True
    idu_lin_ver_jaw_energy.energyMode=False #using jaw pahase (default)
    
    print "    'idu_circ_pos_jaw_energy', 'idu_circ_pos_jaw_energy_follower' - IDU positive circular polarisation jawphase energy and follower"
    idu_circ_pos_jaw_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_circ_pos_energy2jawphase.csv"))
    idu_circ_pos_jaw_energy = EnergyScannableLookup('idu_circ_pos_jaw_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=16, rowphase1=15.1724, rowphase2=0, rowphase3=15.1724, rowphase4=0,
            jawphase_lookup=dict(zip(idu_circ_pos_jaw_table['energy'], idu_circ_pos_jaw_table['jawphase']))
            )
    idu_circ_pos_jaw_energy_maximum=max(idu_circ_pos_jaw_table['energy'])
    idu_circ_pos_jaw_energy_minimum=min(idu_circ_pos_jaw_table['energy'])
    idu_circ_pos_jaw_energy_follower = SilentFollowerScannable('idu_circ_pos_jaw_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_circ_pos_jaw_energy, follower_tolerance=0.35)
    idu_circ_pos_jaw_energy.concurrentRowphaseMoves=True
    idu_circ_pos_jaw_energy.energyMode=False #using jaw pahase (default)

    print "    'idu_circ_neg_jaw_energy', 'idu_circ_neg_jaw_energy_follower' - IDU negative circular polarisation jawphase energy and follower"
    idu_circ_neg_jaw_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_circ_neg_energy2jawphase.csv"))
    idu_circ_neg_jaw_energy = EnergyScannableLookup('idu_circ_neg_jaw_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=16, rowphase1=-15.1724, rowphase2=0, rowphase3=-15.1724, rowphase4=0,
            jawphase_lookup=dict(zip(idu_circ_neg_jaw_table['energy'], idu_circ_neg_jaw_table['jawphase']))
            )
    idu_circ_neg_jaw_energy_maximum=max(idu_circ_neg_jaw_table['energy'])
    idu_circ_neg_jaw_energy_minimum=min(idu_circ_neg_jaw_table['energy'])
    idu_circ_neg_jaw_energy_follower = SilentFollowerScannable('idu_circ_neg_jaw_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_circ_neg_jaw_energy, follower_tolerance=0.35)
    idu_circ_neg_jaw_energy.concurrentRowphaseMoves=True
    idu_circ_neg_jaw_energy.energyMode=False #using jaw pahase (default)

    print "    'idu_lin_hor3_jaw_energy','idu_lin_hor3_energy_follower' - IDU Linear Horizontal polarisation jawphase energy  and follower for 3rd harmonic"
    idu_lin_hor3_jaw_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_hor3_energy2jawphase.csv"))
    idu_lin_hor3_jaw_energy = EnergyScannableLookup('idu_lin_hor3_jaw_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4,
            idu_jawphase, pgm_energy,
            gap=16, rowphase1=0, rowphase2=0, rowphase3=0, rowphase4=0,
            jawphase_lookup=dict(zip(idu_lin_hor3_jaw_table['energy'], idu_lin_hor3_jaw_table['jawphase']))
            )
    idu_lin_hor3_jaw_energy_maximum=max(idu_lin_hor3_jaw_table['energy'])
    idu_lin_hor3_jaw_energy_minimum=min(idu_lin_hor3_jaw_table['energy'])
    idu_lin_hor3_jaw_energy_follower = SilentFollowerScannable('idu_lin_hor3_jaw_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_hor3_jaw_energy, follower_tolerance=0.35)
    idu_lin_hor3_jaw_energy.concurrentRowphaseMoves=True
    idu_lin_hor3_jaw_energy.energyMode=False #using jaw pahase (default)

except:
    localStation_exception(sys.exc_info(), "initialising idu jawphase energy followers")

print "==== idu JAW phase energy scannables done.==== "