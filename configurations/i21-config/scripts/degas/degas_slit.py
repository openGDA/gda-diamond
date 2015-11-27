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
    def __init__(self, slit_to_move_in, slits_to_move_out, front_end_shutter, gauge, gaugemin = 5e-9, gaugemax = 2.5e-8):
        self.slit_to_move_in = slit_to_move_in
        self.slits_to_move_out = slits_to_move_out
        self.front_end_shutter = front_end_shutter
        self.gauge = gauge
        self.gaugemin = gaugemin
        self.gaugemax = gaugemax


    def run(self):
        self.report()

        print "Closing front-end shutter"
        self.front_end_shutter.moveTo('Closed')
        sleep(1)

        print "Moving out slits we do not want to condition"
        [slit.moveTo(0) for slit in self.slits_to_move_out]

        print "Moving in slit to condition"
        self.slit_to_move_in.moveTo(500)

        print "Opening front end shutter"
        self.front_end_shutter.moveTo('Open')
        sleep(1)

        self.report()
        
        try:
            while(True):
                gaugePos = self.gauge.getPosition()
                shutterPos = self.front_end_shutter.getPosition()
                
                print "Pressure = ", self.gauge
                
                if (gaugePos > self.gaugemax and shutterPos == 'Open'):
                    print "Closing front end shutter"
                    self.front_end_shutter.moveTo('Closed')
                    sleep(1)
                elif (gaugePos < self.gaugemin and shutterPos == 'Closed'):
                    print "Opening front end shutter"
                    self.front_end_shutter.moveTo('Open')
                    sleep(1)
                    
                # Wait a second before checking again
                sleep(1)
            
        except KeyboardInterrupt:
            print "Closing down"

        finally:
            print "Closing front-end shutter"
            self.front_end_shutter.moveTo('Closed')
            sleep(1)
            
            print "Moving out slit to condition"
            self.slit_to_move_in.moveTo(0)
            sleep(1)

            self.report()

        
    def report(self):
        print "--------------- DegasSlit ------------------------"
        print "slit_to_move_in = ", self.slit_to_move_in
        print "slits_to_move_out = ", self.slits_to_move_out
        print "front_end_shutter = ", self.front_end_shutter
        print "gauge = ", self.gauge
        print "gaugemin = ", self.gaugemin
        print "gaugemax = ", self.gaugemax
        print "--------------------------------------------------"
