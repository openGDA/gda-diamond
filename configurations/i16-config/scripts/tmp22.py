def lookupScannableName(nameToFind):
	allLabels = dir()
	labels = filter( lambda label : isinstance(eval(label),Scannable) , allLabels )