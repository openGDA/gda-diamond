#
#  Function which creates a header which has the same form as the one created by the GUI Scan5U.
#
def createHeader():
	header = java.util.ArrayList()
	header.add("title")
	header.add("cond1")
	header.add("cond2")
	header.add( "cond3")
	header.add("MonoGrating position: " + `monochromator.getPosition("MonoGrating")`)
	header.add("MonoGrating offset: " + `monochromator.getOffset("MonoGrating")`)
	header.add("MonoMirror position: " + `monochromator.getPosition("MonoMirror")`)
	header.add("MonoMirror offset: " + `monochromator.getOffset("MonoMirror")`)
	header.add("UndulatorGap: " + `undulator.getPosition("UndulatorGap")`)
	header.add("UndulatorMutualPhase position:" + `undulator.getPosition("UndulatorMutualPhase")`)
	return header

#
# Scan specification which uses the createHeader() function. This scan will get the position 
# information as it is at the start of the scan. 
#

stepScan = GridScanMoveToOnly(fixedfocus, 700.0, 800.0, 20.0, 1000.0, "eV")
stepScan.dataHandler.setHeader(createHeader())
stepScan.runScan()

#
# Another example. This one creates the header first and then modifies the title and conditions
#
#

stepScan = GridScanMoveToOnly(fixedfocus, 700.0, 800.0, 20.0, 1000.0,  "eV")
header = createHeader()
header.set(0, "new title")
header.set(1, "one")
header.set(2, "two")
header.set(3,"three")
stepScan.dataHandler.setHeader(header)
stepScan.runScan()

#
# Or you can create the header and add extra strings
#
 
stepScan = GridScanMoveToOnly(fixedfocus, 700.0, 800.0, 20.0, 1000.0, "eV")
header = createHeader()
header.set(0, "header has extra lines")
header.add("a line of special information")
header.add("another line of special information")
stepScan.dataHandler.setHeader(header)
stepScan.runScan()

#
# You really only need to use MultiRegionScan if you have more than one region to do:
#

mrs = MultiRegionScan()
mrs.addScan(GridScanMoveToOnly(fixedfocus, 500.0, 600.0, 20.0, 1000.0, "eV"))
mrs.addScan(GridScanMoveToOnly(fixedfocus, 700.0, 800.0, 20.0, 1000.0, "eV"))
header = createHeader()
header.set(0, "Multi Region Scan")
mrs.dataHandler.setHeader(header)
mrs.runScan()

#
# You can use Jython for loops for multiple repeats. Lines within a particular loop should
# be indented with a tab.  The `i` construction makes a string from a number. This 
# nested pair of for loops will produce four scans.
#

header = createHeader()
header.set(0, "Using for loops")
for i in range(2):
	header.set(1, "outer " + `i`)
	for j in range(2):
		header.set(2, "inner " + `j`)
		stepScan = GridScanMoveToOnly(fixedfocus, 700.0, 800.0, 20.0, 1000.0, "eV")
		stepScan.dataHandler.setHeader(header)
		stepScan.runScan()

