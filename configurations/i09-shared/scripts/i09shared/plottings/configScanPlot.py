'''
Created on 7 Feb 2018

@author: fy65
'''
from gda.configuration.properties import LocalProperties

print("-"*100)
print("Functions and commands for configuring Scan Plot data display: ")
print("    setYFieldVisibleInScanPlot([1,2]) - make 1st and 2nd Y fields visible in scan plot.")
print("    getYFieldVisibleInScanPlot() - return current indices of the Y fields visible in scan plot.")
print("    setXFieldInScanPlot(1) - set the X-field to use in Scan Plot.")
print("    getXFieldInScanPlot() - return the current X-field index in the Scan Plot.")
print("    useSeparateYAxes() - use separate Y Axes for each Y-fields in the Scan Plot.")
print("    useSingleYAxis()  - use the same Y axis for all Y-fields in the Scan Plot.")
print("")

def setYFieldVisibleInScanPlot(indices=[-1]):
    '''
    Set the Y fields visible in Scan Plot using indices starting from 1.
    this setting will be in effect as default until next update.
    @param indices - a list of indices to be visible in the plot
           GAD scan default is -1, means the last index
           0 index means nothing visible
    '''
    LocalProperties.set("gda.plot.ScanPlotSettings.YFieldIndicesVisible", ":".join(map(str, indices)))

def getYFieldVisibleInScanPlot():
    '''
    @return the indices of the current Y fields visible in Scan Plot
    -1 means the last index
    0 means no visible data trace
    '''
    return LocalProperties.getAsIntList("gda.plot.ScanPlotSettings.YFieldIndicesVisible")

def setXFieldInScanPlot(index):
    '''
    @param index to be used for x-axis in the Scan Plot:
    GDA scan default to -1, the last index to be scanned
    '''
    LocalProperties.set("gda.plot.ScanPlotSettings.XFieldIndex", str(index))

def getXFieldInScanPlot():
    '''
    @return the X field currently used as X-axis in the Scan Plot.
    -1 means the last index of scannable to be scanned.
    '''
    return LocalProperties.get("gda.plot.ScanPlotSettings.XFieldIndex")

def useSeparateYAxes():
    '''
    Use separate Y axes for each Y field in the Scan Plot
    '''
    from java.lang import Boolean
    LocalProperties.set("gda.plot.ScanPlotSettings.separateYAxes", Boolean.toString(True))

def useSingleYAxis():
    ''' 
    Use the same Y axis for all Y fields in the Scan Plot
    '''
    from java.lang import Boolean
    LocalProperties.set("gda.plot.ScanPlotSettings.separateYAxes", Boolean.toString(False))
