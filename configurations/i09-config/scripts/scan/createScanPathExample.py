'''
Created on 23 Jan 2014

@author: fy65
'''
from utils.dRangeUtil import drange
from scan.concurrentAnalyserScan import pathscan

xpoints=drange(2.597, 0.203, 0.04728)
#print "x-points: ",xpoints
#ypoints=drange(-552.75, -549.45, 0.1)
#print "y-points: ", ypoints
zpoints=drange(1.152, 3.9, -0.05496)
#print "z-points: ", zpoints
#if len(xpoints) != len(ypoints) or len(xpoints) != len(zpoints):
if len(xpoints) != len(zpoints):
    raise ValueError("The number of path points for each scannables must the same.")
#path=zip(xpoints, ypoints, zpoints)
path=zip(xpoints, zpoints)
print path
scanpath=[]
for l in path:
    scanpath.append(list(l))
scanpath=tuple(scanpath)
print "scan path: ", scanpath

#pathscan((x,y,z), scanpath, sm5iamp8)
