'''
Create IDD energy scannables for different polarisation using ID gap for cvscan and ID tracking
'''
from gdaserver import idd_gap, idd_rowphase1, idd_rowphase2, idd_rowphase3,\
    idd_rowphase4, idd_jawphase, pgm_energy
from lookups.cvs2dictionary import loadCVSTable
from scannable.id_energys.lookupTableDirectory import lookup_tables_dir
from utils.ExceptionLogs import localStation_exception
import sys

print "-"*100

try:
    from Diamond.energyScannableLookup import EnergyScannableLookup
    from scannable.continuous.deprecated.FollowerScannable import SilentFollowerScannable

    print "Creating idd energy and energy follower scannables for different polarisation modes:"
    print "    'idd_circ_pos_energy', 'idd_circ_pos_energy_follower' - IDD positive circular polarisation gap energy and follower"
    idd_circ_pos_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idd_circ_pos_energy2gap.csv"))
    idd_circ_pos_energy = EnergyScannableLookup('idd_circ_pos_energy', idd_gap,
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, idd_jawphase, pgm_energy,
            gap=dict(zip(idd_circ_pos_table['energy'], idd_circ_pos_table['idgap'])),
            rowphase1=dict(zip(idd_circ_pos_table['energy'], idd_circ_pos_table['rowphase1'])), 
            rowphase2=0,
            rowphase3=dict(zip(idd_circ_pos_table['energy'], idd_circ_pos_table['rowphase3'])),
            rowphase4=0, jawphase_lookup=0)
    idd_circ_pos_energy_maximum=max(idd_circ_pos_table['energy'])
    idd_circ_pos_energy_minimum=min(idd_circ_pos_table['energy'])
    idd_circ_pos_energy_follower = SilentFollowerScannable('idd_circ_pos_energy_follower', followed_scannable=pgm_energy, follower_scannable=idd_circ_pos_energy, follower_tolerance=0.35)
    idd_circ_pos_energy.concurrentRowphaseMoves=True
    idd_circ_pos_energy.energyMode=True

    print "    'idd_circ_neg_energy', 'idd_circ_neg_energy_follower' - IDD negative circular polarisation gap energy and follower"
    idd_circ_neg_table=loadCVSTable("%s%s" % (lookup_tables_dir, "/idd_circ_neg_energy2gap.csv"))
    idd_circ_neg_energy = EnergyScannableLookup('idd_circ_neg_energy', idd_gap,
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, idd_jawphase, pgm_energy,
            gap=dict(zip(idd_circ_neg_table['energy'], idd_circ_neg_table['idgap'])),
            rowphase1=dict(zip(idd_circ_neg_table['energy'], idd_circ_neg_table['rowphase1'])), 
            rowphase2=0,
            rowphase3=dict(zip(idd_circ_neg_table['energy'], idd_circ_neg_table['rowphase3'])),
            rowphase4=0, jawphase_lookup=0)
    idd_circ_neg_energy_maximum=max(idd_circ_neg_table['energy'])
    idd_circ_neg_energy_minimum=min(idd_circ_neg_table['energy'])
    idd_circ_neg_energy_follower = SilentFollowerScannable('idd_circ_neg_energy_follower', followed_scannable=pgm_energy, follower_scannable=idd_circ_neg_energy, follower_tolerance=0.35)
    idd_circ_neg_energy.concurrentRowphaseMoves=True
    idd_circ_neg_energy.energyMode=True

    print "    'idd_lin_hor_energy','idd_lin_hor_energy_follower' - IDD Linear Horizontal polarisation gap energy and follower"
    idd_lin_hor_table =loadCVSTable("%s%s" % (lookup_tables_dir, "/idd_lin_hor_energy2gap.csv"))
    idd_lin_hor_energy = EnergyScannableLookup('idd_lin_hor_energy', idd_gap,
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, idd_jawphase, pgm_energy,
            gap=dict(zip(idd_lin_hor_table['energy'], idd_lin_hor_table['idgap'])),
            rowphase1=0, 
            rowphase2=0,
            rowphase3=0,
            rowphase4=0, jawphase_lookup=0)
    idd_lin_hor_energy_maximum=max(idd_lin_hor_table['energy'])
    idd_lin_hor_energy_minimum=min(idd_lin_hor_table['energy'])
    idd_lin_hor_energy_follower = SilentFollowerScannable('idd_lin_hor_energy_follower', followed_scannable=pgm_energy, follower_scannable=idd_lin_hor_energy, follower_tolerance=0.35)
    idd_lin_hor_energy.concurrentRowphaseMoves=True
    idd_lin_hor_energy.energyMode=True

    print "    'idd_lin_ver_energy', 'idd_lin_ver_energy_follower' - IDD Linear Vertical polarisation gap energy and follower"
    idd_lin_ver_table =loadCVSTable("%s%s" % (lookup_tables_dir, "/idd_lin_ver_energy2gap.csv"))
    idd_lin_ver_energy = EnergyScannableLookup('idd_lin_ver_energy', idd_gap,
            idd_rowphase1, idd_rowphase2, idd_rowphase3, idd_rowphase4, idd_jawphase, pgm_energy,
            gap=dict(zip(idd_lin_ver_table['energy'], idd_lin_ver_table['idgap'])),
            rowphase1=24, 
            rowphase2=0,
            rowphase3=24,
            rowphase4=0, jawphase_lookup=0)
    idd_lin_ver_energy_maximum=max(idd_lin_ver_table['energy'])
    idd_lin_ver_energy_minimum=min(idd_lin_ver_table['energy'])
    idd_lin_ver_energy_follower = SilentFollowerScannable('idd_lin_ver_energy_follower', followed_scannable=pgm_energy, follower_scannable=idd_lin_ver_energy, follower_tolerance=0.35)
    idd_lin_ver_energy.concurrentRowphaseMoves=True
    idd_lin_ver_energy.energyMode=True

except:
    localStation_exception(sys.exc_info(), "initialising idd gap energy followers")

print "==== idd GAP energy scannables done.==== "