def run_continuous_scan(bufferedScaler, totalTime, timePerReadout) :
    numReadouts = int(totalTime/timePerReadout)
    bufferedScaler.setUseInternalTriggeredFrames(True)
    cvscan qexafs_energy 0 totalTime numReadouts totalTime bufferedScaler
