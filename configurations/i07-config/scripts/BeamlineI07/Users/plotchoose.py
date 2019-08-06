# Gives the user some control over what is shows/plotted in the 1D plot window
#
# Jonathan Rawle, I07 beamline, September 2011
#
# Columns can either be specified by numbers indicating their position in the scan file
# OR strings can be specified, in which case the previous file is read and the column numbers found from there
#
# yplot - choose which columns are "ticked" to be displayed on the y axis
# yshow - choose which extra columns are shown in the list; all others will be removed (but are still in the data file)
#         call with no arguments to hide all except those plotted
# yreset - resets y axis to standard GDA behaviour
#
# xplot - choose the column to use as the x axis
# xreset - resets the x axis to the GDA default (whatever that is!)

from gda.analysis import ScanFileHolder

def yplot(*args):
    global LocalProperties
    setstring = findCols(args)
    LocalProperties.set("gda.plot.ScanPlotSettings.YFieldIndicesVisible", setstring)

def yshow(*args):
    global LocalProperties
    setstring = findCols(args)
    LocalProperties.set("gda.plot.ScanPlotSettings.YFieldIndicesInvisible", setstring)

def yreset():
    global LocalProperties    
    LocalProperties.clearProperty("gda.plot.ScanPlotSettings.YFieldIndicesVisible")
    LocalProperties.clearProperty("gda.plot.ScanPlotSettings.YFieldIndicesInvisible")

def xreset():
    global LocalProperties
    LocalProperties.set("gda.plot.ScanPlotSettings.XFieldIndex", "-1")

def xplot(*args):
    global LocalProperties
    if len(args) != 1:
        print "Only one column can be used for the X axis"
    else:
        setstring = findCols(args)
        LocalProperties.set("gda.plot.ScanPlotSettings.XFieldIndex", setstring)

def findCols(args):
    # load the data file
    data = ScanFileHolder()
    data.loadSRS(i07.getLastSrsScanFile())
    headings = data.getHeadings()
    retstring = ""

    for i in range(0, len(args)):
        if(type(args[i]) == int):
            retstring += str(args[i]) + " "
        else:
            try:
                retstring += str(headings.index(args[i])) + " "
            except(ValueError):
                print "'" + args[i] + "' not found in last scan"

    return retstring.strip(" ")

alias("yplot")
alias("yshow")
alias("yreset")
alias("xplot")
alias("xreset")
