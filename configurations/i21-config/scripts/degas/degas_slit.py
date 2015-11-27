#----------------------------------------------------------------------------
# Script to degas a single slit
# Move a single slit into position, move the rest out and open the front end
# If the pressure exceeds a given value, close the front end shutter
# and wait for the pressure to drop
#----------------------------------------------------------------------------

from exceptions import KeyboardInterrupt
from time import sleep
from gda.jython import ScriptBase

class DegasSlit:
    def __init__(self, front_end_shutter, gauge, gaugemin = 5e-9, gaugemax = 2.5e-8):
        self.front_end_shutter = front_end_shutter
        self.gauge = gauge
        self.gaugemin = gaugemin
        self.gaugemax = gaugemax


    def run(self):
        self.report()
        
        try:
            while(True):
                gaugePos = self.gauge.getPosition()
                shutterPos = self.front_end_shutter.getPosition()
                
                print "Pressure = ", self.gauge
                
                if (gaugePos > self.gaugemax and shutterPos == 'Open'):
                    print "Closing front end shutter"
                    self.front_end_shutter.moveTo('Closed')
                elif (gaugePos < self.gaugemin and shutterPos == 'Closed'):
                    print "Opening front end shutter"
                    self.front_end_shutter.moveTo('Open')
                    
                # Wait a second before checking again
                sleep(1)
            
        except KeyboardInterrupt:
            print "Closing down"

        finally:
            self.report()

        
    def report(self):
        print "--------------- DegasSlit ------------------------"
        print "front_end_shutter = ", self.front_end_shutter
        print "gauge = ", self.gauge
        print "gaugemin = ", self.gaugemin
        print "gaugemax = ", self.gaugemax
        print "--------------------------------------------------"
