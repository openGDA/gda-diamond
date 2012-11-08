from gda.configuration.properties import LocalProperties

def __getGdaModeProperty():
	mode = str(LocalProperties.get("gda.mode"))
	if mode not in ("live", "dummy"):
		raise ValueError("gda.mode LocalProperty (perhaps via a System property) must be 'live' or 'dummy' not:", mode)
	return mode

def isLive():
	return __getGdaModeProperty()=="live"

def isDummy():
	return __getGdaModeProperty()=="dummy"

def setLoadOldShelf(flag):
	global _loadOldShelf
	_loadOldShelf = flag

def loadOldShelf():
	return _loadOldShelf
