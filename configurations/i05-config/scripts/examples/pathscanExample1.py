
# example creation of a scan in which one or ("slave") axes are linearly dependent on
# another ("master") axis. In this example say and sax are dependent on sapolar
# for each segment of the path, the anchor points of each axis must be specified
 
pst = pathscanTable(mstrAxis='sapolar', mstrStep=2.0, mstrAnchors=[-5,-1,7])
pst.addSlvAxis(slvAxis='say', slvAnchors=[0.1, 0.2, 0.3])
pst.addSlvAxis(slvAxis='sax', slvAnchors=[0.7, 1.2, 2.3])

# print out the table of anchors and steps
print pst

# print out the full scan command so it can be copy&pasted into the Jython console
#pst1.printScan()

# invoke the scan directly
# pst.go()

