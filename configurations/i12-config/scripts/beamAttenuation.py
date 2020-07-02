from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
import scisoftpy as dnp
import time
import math
from gdascripts.utils import caput, caget
from gda.factory import Finder

oh2shtr=Finder.find("oh2shtr")
f1=Finder.find("f1")
f2=Finder.find("f2")

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
        print "Moving Attenuators."
        pos(f1, "clear", f2, "clear")
    elif totalFiltration == 1:
        print "Moving Attenuators."
        pos(f1, "clear", f2, "1mm")
    elif totalFiltration == 2:
        print "Moving Attenuators."
        pos(f1, "2mm", f2, "clear")
    elif totalFiltration == 3:
        print "Moving Attenuators."
        pos(f1, "2mm", f2, "1mm")
    elif totalFiltration == 4:
        print "Moving Attenuators."
        pos(f1, "clear", f2, "4mm")
    elif totalFiltration == 6:
        print "Moving Attenuators."
        pos(f1, "2mm", f2, "4mm")
    elif totalFiltration == 8:
        print "Moving Attenuators."
        pos(f1, "8mm", f2, "clear")
    elif totalFiltration == 9:
        print "Moving Attenuators."
        pos(f1, "8mm", f2, "1mm")
    elif totalFiltration == 12:
        print "Moving Attenuators."
        pos(f1, "8mm", f2, "4mm")
    else:
        print "Chosen attenuation thickness not available."
        print "Possible thickness: 0mm, 1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 9mm or 12mm"
        
    print "Attenuators at requested thickness " + `totalFiltration` + "mm. OH2 shutter closed."
    

print "finished loading 'moveToAttenuation' "
