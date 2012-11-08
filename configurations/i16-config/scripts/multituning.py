import java
from gda.scan import GridScan

def createHeader():
	header = java.util.ArrayList()
	header.add("title")
	header.add("cond1")
	header.add("cond2")
	return header

header = createHeader()
header.set(0, "A Scan with header info")
j = 10
for i in range(j):
	header.set(1, "scan " + `i`)
	header.set(2, " of " + `j`)
	myScan = GridScan(chi, 10, 20, 1)
	myScan.dataHandler.setHeader(header)
	myScan.runScan()


