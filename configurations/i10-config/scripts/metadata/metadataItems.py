'''
Created on 16 Apr 2018

@author: fy65
'''
from gda.jython.commands.GeneralCommands import alias
from gdaserver import idd_gap, idd_rowphase1, idd_jawphase,\
    idd_rowphase3, idd_rowphase4, idd_rowphase2, idd_sepphase, idu_gap,\
    idu_rowphase1, idu_rowphase2, idu_jawphase, idu_rowphase3, idu_rowphase4,\
    idu_sepphase, pgm_grat_pitch, pgm_m2_pitch,pgm_energy
from utils.ExceptionLogs import localStation_exception
import sys
from gda.factory import Finder
try:
    print '-'*80
    print "Define metadata list for data collection:"
    iddmetadatascannables = (idd_gap,idd_rowphase1,idd_rowphase2,idd_rowphase3,idd_rowphase4,idd_jawphase,idd_sepphase)
    idumetadatascannables = (idu_gap,idu_rowphase1,idu_rowphase2,idu_rowphase3,idu_rowphase4,idu_jawphase,idu_sepphase)
    pgmmetadatascannables = (pgm_energy, pgm_grat_pitch, pgm_m2_pitch)

    stdmetadatascannables = iddmetadatascannables + idumetadatascannables + pgmmetadatascannables
    
   
    #Nexus file
    print "-"*50
    print "Nexus file metadata commands:"
    print "    'meta_add' - add a scannable or scannables to the scan metadata"
    print "    'meta_ll'  - list the items and their values to be put into the scan metadata"
    print "    'meta_ls'  - list only the items to be put into the scan metadata"
    print "    'meta_rm'  - remove a scannable or scannables from the scan metadata"
    from metashop import *  # @UnusedWildImport
    for each in stdmetadatascannables:
        meta_add(each)
    
except:
    localStation_exception(sys.exc_info(), "creating metadata objects")
