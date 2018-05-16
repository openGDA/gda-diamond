'''
Usage:
    1. run this script from jython editor, you will have an object called 'pathscan'
    2. start your scan using
    >>>pathscan("/path/to/your/input/scan_path_data_file")
    
    pathYour scan path data file must be in the format as (tab or space delimited)

#SScanSS project file: example.hdf
First line:     1
Last line:     10
ScannableNames    ss2.x    ss2.z    ss2.y    ss2.rx    ss2.theta    edxd
ScannableUnits    mm    mm    mm    deg    deg    s
1    3.25714    74.5914    0    0    2.50032    1.1
2    1.62857    37.2957    -0.00011139    0    2.50032    2.0
3    0    0    0    0    2.50032    3.3
4    -1.62857    -37.2957    0    0    2.50032    4.4
5    -3.25714    -74.5914    0    0    2.50032    5.5
6    -39.5623    1.72753    0.0199849    0    2.50032    6.6
7    -19.891    0.868553    0.0199584    0    2.50032    7.7
8    -0.219791    0.0095771    0.0201187    0    2.50032    8.8
9    19.4515    -0.849398    0.0197406    0    2.50032    9.9
10    39.1227    -1.70837    0.0200012    0    2.50032    10.0

Created on 7 Oct 2011

@author: fy65
'''
# load in scan path data
import string
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.jython.commands.ScannableCommands import scan

class PathScan():
    def __init__(self, name):
        self.name=name
        self.sg = ScannableGroup()
        self.pointid=[]
        self.path=[]
        self.startline=1
        self.lastline=10
        self.scannablelist=[]
        self.scannableunitlist=[]
        self.detector=edxd #@UndefinedVariable
        self.detectorunit="s"
        self.exposuretime=[]
        
    def read_scan_path(self,filename):
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        lines = map(string.split, map(string.strip, lines))
        self.pointid=[]
        self.path=[]
        self.scannablelist=[]
        self.scannableunitlist=[]
        self.exposuretime=[]
        # parsing the input data
        for line in lines:
            print line
            if line[0].startswith("#"):     #ignore comment
                continue
            elif line[0].startswith("First"):
                self.startline=line[2]
            elif line[0].startswith("Last"):
                self.lastline=line[2]
            elif line[0].startswith("ScannableNames"):
                self.scannablelist=[globals()[x] for x in line[1:-1]] # get all motors
                self.sg.setName("ss2path")
                self.sg.setGroupMembers(self.scannablelist)
                self.sg.configure()
                self.detector=globals()[line[-1]]                    # get detector
            elif line[0].startswith("ScannableUnits"):
                self.scannableunitlist=[x for x in line[1:-1]]
                self.detectorunit=line[-1]
            else: #real data go here
                self.pointid.append(int(line[0]))
                self.path.append([float(line[1]),float(line[2]),float(line[3]),float(line[4]),float(line[5])])
                self.exposuretime.append(float(line[6]))
    
    def start(self,filename, exposureTime):
        self.read_scan_path(filename)
        print self.pointid
        print self.path
        print self.exposuretime
        pathPositions=tuple(self.path)
        print pathPositions
        scan self.sg pathPositions self.detector exposureTime
        # follow method need to sort out data save to a file which I donot know edxd well enough to do manually so have to use scan method above
        #index = self.startline
        #try:
            #for point in self.path[self.startline:self.lastline+1]:
                #print ("%s - %s %d") % (self.getName(), "move to point", index)
                #self.sg.asynchronousMoveTo(point[:-1])
                #self.sg.waitWhileBusy()
                #print ("%s - %s %d") % (self.getName(), "collect data at point", index)
                #self.detector.setCollectionTime(point[-1])
                #self.detector.collectData()
                #index=index+1
                #interruptable() #@UndefinedVariable enable user to abort the scan processing
        #except:
            #print ("%s - %s") % (self.getName(),"scan aborted")
            #raise
        #else:
            #print ("%s - %s") % (self.getName(),"scan completed")
            
    def setName(self, name):
        self.name=name
        
    def getName(self):
        return self.name
    
pathscan=PathScan("pathscan")
