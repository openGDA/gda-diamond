from gdascripts.testing.livetest.AllScannablesTestGroup import AllScannablesTestGroup
from gdascripts.testing.livetest.FileAccessPermissionsTestGroup import FileAccessPermissionsTestGroup
from gdascripts.testing.livetest.ExtendedSyntaxCommandTestGroup import ExtendedSyntaxCommandTestGroup
from gdascripts.scan.gdascans import Scan
from gdascripts.analysis.datasetprocessor.oned.TwoGaussianEdges import TwoGaussianEdges
from gdascripts.scan.process.ScannableScan import ScannableScan

import time
from gda.jython.commands.InputCommands import requestInput as raw_input

# Header
print "#*"*40
print "liveBeamlineTestsB16Simulation"
print "started at: ", time.asctime()
print "#*"*40


################ Test and configure diffcalc ##############
esctg = ExtendedSyntaxCommandTestGroup()

esctg.addCommand("newub 'b16_270608'")
esctg.addCommand("setlat 'xtal' 3.8401 3.8401 5.43072")
esctg.addCommand("pos energy 12.39842/1.24")
esctg.addCommand("pos fivec, [5.000 22.790 1.552 22.400 14.255]")
esctg.addCommand("addref 1 0 1.0628")
esctg.addCommand("pos fivec [5.000 22.790 4.575 24.275 101.320]")
esctg.addCommand("addref 0 1 1.0628")
esctg.addCommand("checkub")
esctg.test()


################ Test All Scannables ##############
raw_input("Press return to test all scannables")

astg=AllScannablesTestGroup(globals())
#astg.addNameToSkip('y')
astg.test()

############### Test file permissions #############
#pass

#################### Gda Commands ###################
esctg = ExtendedSyntaxCommandTestGroup()

esctg.addPrompt("Press return: Basic commands")
esctg.addCommand("print 1")
esctg.addCommand("pos x")
esctg.addCommand("x")
esctg.addCommand("scan x 1 3 1")


#esctg.addCommand("some_variable = 123456789")
#esctg.addCommand("print some_variable")

# focus finding with wire
esctg.addPrompt("Press return: pos wirescanner")
wirescanner = ScannableScan('wirescanner', TwoGaussianEdges(), Scan, tbdiagY, -3.8500, -3.999500, 0.0005, tbdiagZcoarse, rc, pips2, .2) #@UndefinedVariable
esctg.addCommand("pos wirescanner")

esctg.addPrompt("Press return: scan wirescanner")
esctg.addCommand("scan tbdiagZcoarse 153 154 1 wirescanner")
esctg.addCommand("minval")
esctg.addCommand("go minval")

esctg.addPrompt("Press return: Find focus with detector")
esctg.addCommand("scan x 430 600 20 ipp 20 peak2d")
esctg.addCommand("go minval")
esctg.addCommand("assert x() == 490")
esctg.addCommand("rscan x -20 20 2.5 ipp 20 peak2d")
esctg.addCommand("go minval")
esctg.addCommand("assert x() == 482.5")
esctg.test()

