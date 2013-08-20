
def createHeader():
	header = java.util.ArrayList()
	header.add("title")
	header.add("cond1")
	header.add("cond2")
	header.add( "cond3")
	return header



header = createHeader()
header.set(0, "Multiple Undulator Tuning Scans")
j = 100
for i in range(j):
	header.set(1, "scan " + `i`)
	header.set(2, " of " + `j`)
	stepScan = UndulatorTuningGridScan(fixedfocus, 700.0, 800.0, 10.0, 1000.0, "eV", undulatorenergy, "EveryPoint")
	stepScan.dataHandler.setHeader(header)
	stepScan.runScan()


