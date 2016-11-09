# Scripts to control shutters
# These are used by the status view in the client.
import time
from gda.factory import Finder
from gda.jython.commands.ScannableCommands import pos

print "Defining shutter controls"

finder = Finder.getInstance()

def toggle_oh1_shtr():
    oh1_shutter_status = finder.find("oh1_shutter_status")
    if oh1_shutter_status() == "Open":
        pos(oh1_shutter_status, "Close")
    else:
        pos(oh1_shutter_status,"Reset")
        time.sleep(3)
        pos(oh1_shutter_status, "Open")

def toggle_oh2_shtr():
    oh2_shutter_status = finder.find("oh2_shutter_status")
    if oh2_shutter_status() == "Open":
        pos(oh2_shutter_status, "Close")
    else:
        pos(oh2_shutter_status,"Reset")
        time.sleep(3)
        pos(oh2_shutter_status, "Open")

def toggle_oh3_shtr():
    oh3_shutter_status = finder.find("oh3_shutter_status")
    if oh3_shutter_status() == "Open":
        pos(oh3_shutter_status, "Close")
    else:
        pos(oh3_shutter_status,"Reset")
        time.sleep(3)
        pos(oh3_shutter_status, "Open")

def toggle_eh2_nano_shtr():
    eh2_nano_shutter_status = finder.find("eh2_nano_shutter_status")
    if eh2_nano_shutter_status() == "Open":
        pos(eh2_nano_shutter_status, "Close")
    else:
        pos(eh2_nano_shutter_status,"Reset")
        time.sleep(3)
        pos(eh2_nano_shutter_status, "Open")