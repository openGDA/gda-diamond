'''
Created on 7 Oct 2011

@author: fy65
'''
# load in scan path data
import string
from gda.device.scannable.scannablegroup import ScannableGroup
#from gda.jython.commands.ScannableCommands import scan

sg = ScannableGroup()
times=[]
pointid=[]
path=[]
startline=1
lastline=10
scannablelist=[]
scannableunitlist=[]
detector=edxd #@UndefinedVariable
detectorunit="s"

def read_scan_path(filename):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    lines = map(string.split, map(string.strip, lines))
    # parsing the input data
    for line in lines:
        if line[0].startswith("#"):     #ignore comment
            continue
        elif line[0].startswith("First"):
            startline=line[2]
        elif line[0].startswith("Last"):
            lastline=line[2]
        elif line[0].startswith("ScannableNames"):
            scannablelist=[globals()[x] for x in line[1:-1]] # get all motors
            sg.setGroupMembers(scannablelist)
            detector=globals()[line[-1]]                    # get detector
        elif line[0].startswith("ScannableUnits"):
            scannableunitlist=[globals()[x] for x in line[1:-1]]
            detectorunit=line[-1]
        else: #real data go here
            for each in line:
                pointid.append(each[0])
                path.append(each[1:])

def pathscan(filename):
    read_scan_path(filename)
    #scan(sg, path,detector, times)
    for point in path[startline:lastline+1]:
        sg.asynchronousMoveTo(point[:-1])
        sg.waitWhileBusy()
        detector.setCollectionTime(point[-1])
        detector.collectData()
        interruptable() #@UndefinedVariable enable user to abort the scan processing
            
        

    

