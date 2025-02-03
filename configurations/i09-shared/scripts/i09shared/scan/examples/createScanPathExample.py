'''
Created on 23 Jan 2014

@author: fy65
'''
from i09shared.utils.dRangeUtil import drange
from gdascripts.scan.pathscanCommand import pathscan #@UnusedImport

xpoints=drange(10, 20, 1)
#print "x-points: ",xpoints
ypoints=drange(20, 30, 1)
#print "y-points: ", ypoints
zpoints=drange(30, 40, 1)
#print "z-points: ", zpoints
if len(xpoints) != len(ypoints) or len(xpoints) != len(zpoints):
    raise ValueError("The number of path points for each scannables must the same.")
path=zip(xpoints, ypoints, zpoints)
scanpath=[]
for l in path:
    scanpath.append(list(l))
scanpath=tuple(scanpath)
print "scan path: ", scanpath

# usages example
# pathscan((x,y,z), scanpath, sm5iamp8)