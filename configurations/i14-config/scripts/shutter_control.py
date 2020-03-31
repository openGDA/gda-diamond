# Scripts to control shutters
# These are used by the status view in the client.
import time
from gdaserver import oh1_shutter_status, oh2_shutter_status, oh3_shutter_status, eh2_nano_shutter_status
from gda.jython.commands.ScannableCommands import pos

print("Defining shutter controls")

def toggle_oh1_shtr():
    if oh1_shutter_status() == "Open":
        pos(oh1_shutter_status, "Close")
    else:
        pos(oh1_shutter_status,"Reset")
        time.sleep(3)
        pos(oh1_shutter_status, "Open")

def toggle_oh2_shtr():
    if oh2_shutter_status() == "Open":
        pos(oh2_shutter_status, "Close")
    else:
        pos(oh2_shutter_status,"Reset")
        time.sleep(3)
        pos(oh2_shutter_status, "Open")

def toggle_oh3_shtr():
    if oh3_shutter_status() == "Open":
        pos(oh3_shutter_status, "Close")
    else:
        pos(oh3_shutter_status,"Reset")
        time.sleep(3)
        pos(oh3_shutter_status, "Open")

def open_eh2_nano_shtr():
    if not eh2_nano_shutter_status() == "Open":
        pos(eh2_nano_shutter_status,"Reset")
        time.sleep(3)
        pos(eh2_nano_shutter_status, "Open")

def toggle_eh2_nano_shtr():
    if eh2_nano_shutter_status() == "Open":
        pos(eh2_nano_shutter_status, "Close")
    else:
        open_eh2_nano_shtr()