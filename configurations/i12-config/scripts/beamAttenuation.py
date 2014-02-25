from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
import scisoftpy as dnp
import time
import math
from gdascripts.utils import caput, caget
from gda.factory import Finder

finder = Finder.getInstance()

oh2shtr=finder.find("oh2shtr")


# Additional information:
# filter 1:
#    0:2mm
#    1:0mm
#    2:8mm
    
# filter2:
#    0:1mm
#    1:0mm
#    2:4mm



def moveToAttenuation(totalFiltration):
    print "Requested totalFiltration = " + `totalFiltration` 
        
    print "Closing OH2 shutter."
    pos(oh2shtr, "Close")
    print "Shutter now closed."
    if totalFiltration == 0:
        pos f1 "Clear" f2 "1mm"
        print "Moving Attenuators."
    if totalFiltration = 1:
        pos f1 1 f2 0
        print "Moving Attenuators."
    if totalFiltration = 2:
        pos f1 0 f2 1
        print "Moving Attenuators."
    if totalFiltration = 3:
        pos f1 0 f2 0
        print "Moving Attenuators."
    if totalFiltration = 4:
        pos f1 1 f2 2
        print "Moving Attenuators."
    if totalFiltration = 6:
        pos f1 0 f2 2
        print "Moving Attenuators."
    if totalFiltration = 8:
        pos f1 2 f2 1
        print "Moving Attenuators."
    if totalFiltration = 9:
        pos f1 2 f2 0
        print "Moving Attenuators."
    if totalFiltration = 12:
        pos f1 2 f2 2
        print "Moving Attenuators."
    else:
        print "Chosen attenuation thickness not available."
        print "Possible thickness: 0mm, 1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 9mm or 12mm"
        
    print "Attenuators at requested thickness " + `totalThickness` + "mm. OH2 shutter closed."
    

print "finished loading 'moveToAttenuation' "
