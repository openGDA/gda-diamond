print "Adding continuous scan commands for ionchambers and xspress3 "
print "\t run_continuous_scan(totalTime, timePerReadout) \n\t run_continuous_xspress3_scan(totalTime, timePerReadout) "

def run_continuous_scan(totalTime, timePerReadout) :
    numReadouts = int(totalTime/timePerReadout)
    ionchambers.setUseInternalTriggeredFrames(True)
    cvscan qexafs_energy 0 totalTime numReadouts totalTime ionchambers

def run_continuous_xspress3_scan(totalTime, timePerReadout) :
    numReadouts = int(totalTime/timePerReadout)
    ionchambers.setUseInternalTriggeredFrames(True)
    cvscan qexafs_energy 0 totalTime numReadouts totalTime buffered_xspress3 ionchambers