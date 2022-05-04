'''
A module that add additional Scan Listener to Standard GDA scan commands

Created on Apr 29, 2022

@author: fy65
'''

print("-"*100)
# print("Switch off scan processor by default at Sarnjeet's request on 11 May 2016 in I06-1.")    
print(" To manually switch on scan processor, run 'scan_processing_on()' function on Jython Terminal.")
print(" To manually switch off scan processor, run 'scan_processing_off()' function on Jython Terminal.")

from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor_normal_processes = scan_processor.processors
scan_processor_empty_processes  = []
 
def scan_processing_on():
    scan_processor.processors = scan_processor_normal_processes
 
def scan_processing_off():
    scan_processor.processors = scan_processor_empty_processes
scan_processing_off()

from i06shared.elog.scanToElogPost import ElogPosterScanListener
post_to_elog = ElogPosterScanListener()
#enable post to elog
ascan  = specscans.Ascan([scan_processor, post_to_elog])
a2scan = specscans.A2scan([scan_processor, post_to_elog])
a3scan = specscans.A3scan([scan_processor, post_to_elog])
mesh   = specscans.Mesh([scan_processor, post_to_elog])
dscan  = specscans.Dscan([scan_processor, post_to_elog])
d2scan = specscans.D2scan([scan_processor, post_to_elog])
d3scan = specscans.D3scan([scan_processor, post_to_elog])
scan = gdascans.Scan([scan_processor, post_to_elog])
rscan = gdascans.Rscan([scan_processor, post_to_elog])
cscan = gdascans.Cscan([scan_processor, post_to_elog])