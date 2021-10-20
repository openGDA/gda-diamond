'''
Create IDU energy scannables for different polarisation using ID gap for cvscan and ID tracking
'''
from gdaserver import idu_gap, idu_rowphase1, idu_jawphase, idu_rowphase2,\
    idu_rowphase3, idu_rowphase4, pgm_energy
from lookups.cvs2dictionary import loadCVSTable
from utils.ExceptionLogs import localStation_exception
import sys
from scannable.id_energys.lookupTableDirectory import lookup_tables_dir

print "-"*100

try:
    from Diamond.energyScannableLookup import EnergyScannableLookup
    from scannable.continuous.deprecated.FollowerScannable import SilentFollowerScannable

    print "Creating idu gap energy and gap energy follower scannables for different polarisation modes:"
    print "    'idu_circ_pos_energy', 'idu_circ_pos_energy_follower' - IDU positive circular polarisation gap energy and follower"
    idu_circ_pos_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_circ_pos_energy2gap.csv"))
    idu_circ_pos_energy = EnergyScannableLookup('idu_circ_pos_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=dict(zip(idu_circ_pos_table['energy'], idu_circ_pos_table['idgap'])),
            rowphase1=dict(zip(idu_circ_pos_table['energy'], idu_circ_pos_table['rowphase1'])),
            rowphase2=0,
            rowphase3=dict(zip(idu_circ_pos_table['energy'], idu_circ_pos_table['rowphase3'])),
            rowphase4=0, jawphase_lookup=0)
    idu_circ_pos_energy_maximum=max(idu_circ_pos_table['energy'])
    idu_circ_pos_energy_minimum=min(idu_circ_pos_table['energy'])
    idu_circ_pos_energy_follower = SilentFollowerScannable('idu_circ_pos_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_circ_pos_energy, follower_tolerance=0.35)
    idu_circ_pos_energy.concurrentRowphaseMoves=True
    idu_circ_pos_energy.energyMode=True
    
    print "    'idu_circ_neg_energy', 'idu_circ_neg_energy_follower' - IDU negative circular polarisation gap energy and follower"
    idu_circ_neg_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_circ_neg_energy2gap.csv"))
    idu_circ_neg_energy = EnergyScannableLookup('idu_circ_neg_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=dict(zip(idu_circ_neg_table['energy'], idu_circ_neg_table['idgap'])),
            rowphase1=dict(zip(idu_circ_neg_table['energy'], idu_circ_neg_table['rowphase1'])),
            rowphase2=0,
            rowphase3=dict(zip(idu_circ_neg_table['energy'], idu_circ_neg_table['rowphase3'])),
            rowphase4=0, jawphase_lookup=0)
    idu_circ_neg_energy_maximum=max(idu_circ_neg_table['energy'])
    idu_circ_neg_energy_minimum=min(idu_circ_neg_table['energy'])
    idu_circ_neg_energy_follower = SilentFollowerScannable('idu_circ_neg_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_circ_neg_energy, follower_tolerance=0.35)
    idu_circ_neg_energy.concurrentRowphaseMoves=True
    idu_circ_neg_energy.energyMode=True
    
    print "    'idu_lin_hor_energy','idu_lin_hor_energy_follower' - IDU Linear Horizontal polarisation gap energy and follower"
    idu_lin_hor_table =loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_hor_energy2gap.csv"))
    idu_lin_hor_energy = EnergyScannableLookup('idu_lin_hor_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=dict(zip(idu_lin_hor_table['energy'], idu_lin_hor_table['idgap'])),
            rowphase1=0, 
            rowphase2=0,
            rowphase3=0,
            rowphase4=0, jawphase_lookup=0)
    idu_lin_hor_energy_maximum=max(idu_lin_hor_table['energy'])
    idu_lin_hor_energy_minimum=min(idu_lin_hor_table['energy'])
    idu_lin_hor_energy_follower = SilentFollowerScannable('idu_lin_hor_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_hor_energy, follower_tolerance=0.35)
    idu_lin_hor_energy.concurrentRowphaseMoves=True
    idu_lin_hor_energy.energyMode=True
    
    print "    'idu_lin_ver_energy', 'idu_lin_ver_energy_follower' - IDU Linear Vertical polarisation gap energy and follower"
    idu_lin_ver_table =loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_ver_energy2gap.csv"))
    idu_lin_ver_energy = EnergyScannableLookup('idu_lin_ver_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=dict(zip(idu_lin_ver_table['energy'], idu_lin_ver_table['idgap'])),
            rowphase1=24, 
            rowphase2=0,
            rowphase3=24,
            rowphase4=0, jawphase_lookup=0)
    idu_lin_ver_energy_maximum=max(idu_lin_ver_table['energy'])
    idu_lin_ver_energy_minimum=min(idu_lin_ver_table['energy'])
    idu_lin_ver_energy_follower = SilentFollowerScannable('idu_lin_ver_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_ver_energy, follower_tolerance=0.35)
    idu_lin_ver_energy.concurrentRowphaseMoves=True
    idu_lin_ver_energy.energyMode=True

    print "    'idu_lin_hor3_energy','idu_lin_hor3_energy_follower' - IDU Linear Horizontal polarisation gap energy  and follower for 3rd harmonic"
    idu_lin_hor3_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idu_lin_hor3_energy2gap.csv"))
    idu_lin_hor3_energy = EnergyScannableLookup('idu_lin_hor3_energy', idu_gap,
            idu_rowphase1, idu_rowphase2, idu_rowphase3, idu_rowphase4, idu_jawphase, pgm_energy,
            gap=dict(zip(idu_lin_hor3_table['energy'], idu_lin_hor3_table['idgap'])),
            rowphase1=0, 
            rowphase2=0,
            rowphase3=0,
            rowphase4=0, jawphase_lookup=0)
    idu_lin_hor3_energy_maximum=max(idu_lin_hor3_table['energy'])
    idu_lin_hor3_energy_minimum=min(idu_lin_hor3_table['energy'])
    idu_lin_hor3_energy_follower = SilentFollowerScannable('idu_lin_hor3_energy_follower', followed_scannable=pgm_energy, follower_scannable=idu_lin_hor3_energy, follower_tolerance=0.35)
    idu_lin_hor3_energy.concurrentRowphaseMoves=True
    idu_lin_hor3_energy.energyMode=True

except:
    localStation_exception(sys.exc_info(), "initialising idu gap energy followers")

print "==== idu_GAP energy scannables done.==== "