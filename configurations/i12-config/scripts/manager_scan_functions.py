from uk.ac.gda.client.tomo.basic.beans import BasicTomographyParameters
from tomo_basic import basicTomoScanFromBean
from manager_scan import ScanManager

sm = ScanManager()  
           
def runNextScan():     
    scanparams = sm.nextScan()
    if isinstance(scanparams, BasicTomographyParameters ) :
        basicTomoScanFromBean(scanparams) 
    else :
        print "not a recognised scan"