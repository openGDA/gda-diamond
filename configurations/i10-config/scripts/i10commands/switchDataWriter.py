'''
Created on 1 Mar 2018

@author: fy65
'''
from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import alias

print "-"*100
print "Create data file format commands:"
print "    1. 'nexusformat' - switch to write Nexus data file. This is GDA default data file format."
print "    2. 'asciiformat' - switch to write ASCII data file. This format is being deprecated!"
print "    3. 'whichformat' - query which data file format is set in GDA currently."

def nexusformat():
    LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "NexusScanDataWriter")
    
def asciiformat(namespace=globals()):
    LocalProperties.set(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT, "SrsDataFile")
    print("Setup metadata list for data collection:")
    metadatalist=[]
    iddlist = [idd_gap,idd_rowphase1,idd_rowphase2,idd_rowphase3,idd_rowphase4,idd_jawphase,idd_sepphase]  # @UndefinedVariable
    idulist = [idu_gap,idu_rowphase1,idu_rowphase2,idu_rowphase3,idu_rowphase4,idu_jawphase,idu_sepphase]  # @UndefinedVariable
    pgmlist = [pgm_energy, pgm_grat_pitch, pgm_m2_pitch]  # @UndefinedVariable
    
    metadatalist=metadatalist+iddlist+idulist+pgmlist
    try:
        print("-"*50)
        print("SRS or ASCII file metadata command:")
        from gdascripts.scannable.installStandardScannableMetadataCollection import addmeta, lsmeta, meta, rmmeta, setmeta, note  # @UnusedImport
        meta.rootNamespaceDict=namespace
        note.rootNamespaceDict=namespace
        def stdmeta():
            setmeta_ret=setmeta(*metadatalist)
            print("Standard metadata scannables: " + setmeta_ret)
        stdmeta()
        print("    Use 'stdmeta' to reset to standard scannables")
        alias('stdmeta')
        add_default(meta)  # @UndefinedVariable
        meta.quiet = True
    except:
        from utils.ExceptionLogs import localStation_exception
        localStation_exception(sys.exc_info(), "creating SRS file metadata objects")
        
def whichformat():
    return LocalProperties.get(LocalProperties.GDA_DATA_SCAN_DATAWRITER_DATAFORMAT)

alias("nexusformat")
alias("asciiformat")
alias("whichformat")

