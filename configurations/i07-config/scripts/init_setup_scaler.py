###############################################################################
###                       Devices connected to scaler 1                     ###
###         			Rob Walton, 20090807                                ###
###  modified from b16 scaler setup in config-b16/scripts/localStation.py   ###
###############################################################################

from gdascripts.scannable.detector.ScalerSubsetScannable import ScalerSubsetScannable
struckRootPv = "BL07I-EA-DET-01:"
def assignStruckChannel(channelNo, nameList, namespace):
	allNames = ''
	for name in nameList:
		namespace[name] = ScalerSubsetScannable(name,struck1,[channelNo])
		allNames += name + '/'
	allNames = allNames[:-1]

	print "ch%i: %s" % (channelNo, allNames)
	cac = CAClient(struckRootPv+'SCALER.NM%i' % channelNo)
	cac.configure()
	cac.caput(allNames)
	cac.clearup()

	
print "ch   gda-name"
assignStruckChannel(1, ['ct1','cttime'], globals())
assignStruckChannel(2, ['ct2', 'cyber'], globals())
assignStruckChannel(3, ['ct3'], globals())
assignStruckChannel(4, ['ct4'], globals())
assignStruckChannel(5, ['ct5'], globals())
assignStruckChannel(6, ['ct6'], globals())
assignStruckChannel(7, ['ct7'], globals())
assignStruckChannel(8, ['ct8'], globals())