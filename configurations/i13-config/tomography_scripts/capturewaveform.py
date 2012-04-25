#!/bin/env dls-python2.6
import os, sys, csv
from pprint import *
from pkg_resources import require
require('cothread')

import cothread
from cothread.catools import *

class RecordWaveform:
    def __init__(self, waveformpv, numcapture=0, numsamples=0):
        self.pv = waveformpv
        self.data = []
        self.cahandle = None
        self.numcapture = numcapture
        self.count = 0
        self.num_samples=numsamples
        
    def busy(self):
        if self.cahandle == None:
            return False
        else:
            return True
            
    def wait(self):
        print "Wait..."
        while( self.busy() ):
            cothread.Sleep(0.1)
        
    def connect(self):
        print "Connect"
        if self.cahandle == None:
            self.cahandle = camonitor( self.pv, self.callback, format=FORMAT_TIME, count=self.num_samples)
            
    def disconnect(self):
        print "Disconnect"
        if self.cahandle != None:
            self.cahandle.close()
            self.cahandle = None
    
    def callback(self, value):
        # if everything nok OK, disconnect
        if not value.ok:
            print "Callback error. Closing down."
            self.disconnect()
            return
            
        print "Callback: num_elements=%d num_updates=%d timestamp=%s" %(len(value), value.update_count, str(value.timestamp))
        self.data += [value]
        self.count += 1
        if (self.numcapture > 0):
            if (self.count >= self.numcapture):
                self.disconnect()
    
    def dump(self):
        print "pretty print"
        pprint( self.data )
        
    def dump_to_csv_file(self, filename):
        print "Dumping to CSV file"
        # First transpose the data so we get rows of samples
        rows = zip(*self.data)
        writer = csv.writer( open(filename, 'w') )
        writer.writerows( rows )
        
        
def main():
    recw = RecordWaveform( "BL12I-EA-ADC-01:WAVE:00", numcapture=10)
    recw.connect()
    recw.wait()
    recw.dump()
    recw.dump_to_csv_file( "adc.csv" )
    
if __name__=="__main__":
    main()
    
    
    
