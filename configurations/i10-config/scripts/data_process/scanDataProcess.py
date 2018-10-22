'''
Created on 10 Apr 2018

@author: fy65
'''
from gdascripts.scan.installStandardScansWithProcessing import scan_processor
print "-"*100

scan_processor_normal_processes = scan_processor.processors
scan_processor_empty_processes  = []

def scan_processing_on():
    scan_processor.processors = scan_processor_normal_processes
 
def scan_processing_off():
    scan_processor.processors = scan_processor_empty_processes
print
print "Switch off scan processor by default !!!"    
print " To manually switch on scan processor, run 'scan_processing_on()' function on Jython Terminal."
print " To manually switch off scan processor, run 'scan_processing_off()' function on Jython Terminal."
scan_processing_off()