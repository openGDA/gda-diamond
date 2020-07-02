"""
Factory for creating open/close commands for shutters and valves
for use with GDA at Diamond Light Source
"""

#from gdascripts.messages.handle_messages import simpleLog
from time import sleep

"""
beamline = Finder.find("Beamline")
shopen = EpicsPneumaticShutterFactory(beamline, "EH Shutter", "-PS-SHTR-02", True)
shclose = EpicsPneumaticShutterFactory(beamline, "EH Shutter", "-PS-SHTR-02", False)
"""
def EpicsPneumaticShutterFactory(beamline, desc, pv, opener):
    controlPV, controlReset, controlOpen, controlClose = pv + ":CON", 2, 0, 1
    statusPV, statusOpen, statusClosed = pv + ":STA", '1', '3'
    
    def EpicsPneumaticShutter():
        """
        EpicsPneumaticShutter does:
            1. Opens the experimental hutch shutter.
            2. Waits for it to open.
            3. Checks the shutter status.
        syntax: openEHShutter()
        """
        beamline.setValue("Top", controlPV, controlReset)
        if opener:
            beamline.setValue("Top", controlPV, controlOpen)
            #simpleLog( "Opening " + desc + "...")
            waitfor = statusOpen
        else:
            beamline.setValue("Top", controlPV, controlClose)
            #simpleLog( "Closing " + desc + "...")
            waitfor = statusClosed
        
        for _ in range(6):
            status = beamline.getValue(None, "Top", statusPV)
            if status == waitfor:
                break
            sleep(1)
        
        if (status != waitfor):
            #simpleLog( " -> Time out: Could not " + desc + " shutter")
            return " -> Time out: Could not " + ("Open " if opener else "Close ") + desc + "."
        elif (status == statusOpen):
            #simpleLog( " -> Shutter Open")
            return " -> " + desc + " Open."
        elif (status == statusClosed):
            #simpleLog( " -> Shutter Closed")
            return " -> " + desc + " Closed."
    
    return EpicsPneumaticShutter