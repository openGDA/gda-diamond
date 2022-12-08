import sys

limaCcd = frelon.getLimaCcd()

def showInfo(infoString, command) :
    result = eval(command)
    print infoString,",",command,"\t:",result,"\n"

def showFrelonState() :
    showInfo("Accumulation mode", "limaCcd.getAcqMode()" )
    showInfo("Number of images to be acquired", "limaCcd.getAcqNbFrames()" )
    showInfo("Trigger mode", "limaCcd.getAcqTriggerMode()" )
    showInfo("Accumulation time mode", "limaCcd.getAccTimeMode()" )
    showInfo("Max exposure time per accumulation", "limaCcd.getAccMaxExpoTime()" )
    showInfo("Exposure time of image", "limaCcd.getAcqExpoTime()" )


def resetFrelonToInternalTriggerMode() :
    try :
        triggerMode = limaCcd.AcqTriggerMode.INTERNAL_TRIGGER
        #triggerMode = limaCcd.AcqTriggerMode.EXTERNAL_TRIGGER
        print "Stopping frelon and resetting trigger mode to internal..."
        frelon.stop()
        frelon.getDetectorData().setTriggerMode(triggerMode)
        limaCcd.setAcqTriggerMode(triggerMode)
        print "Done"
    except :
        print "Problem resetting frelon trigger mode : ",sys.exc_info()[0]