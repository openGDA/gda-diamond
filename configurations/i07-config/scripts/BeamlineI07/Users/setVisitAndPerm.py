from copy import deepcopy

_setVisit = deepcopy(setVisit)
del setvisit

def setVisit(visit):
	_setVisit(visit)
	i07userperm(visit)
	setDir("")
	print("- Detector filepaths")
	print("pilatus2: {}".format(pil2.getFilePath()))
	print("pilatus3: {}".format(pil3.getFilePath()))
