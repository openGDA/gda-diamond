from gdascripts.scan.pathscanCommand import create_pathgroup
from gda.jython.commands.ScannableCommands import scan
from gda.jython.commands.GeneralCommands import alias

def pathscan(scannables, path, detector, exposure, *args):
    ''' Scan a group of scannables following the specified path and collect data at each point from specified detector and time'''
    pathgroup = create_pathgroup(scannables)
    scan([pathgroup, path, detector, exposure]+list(args))

alias("pathscan")