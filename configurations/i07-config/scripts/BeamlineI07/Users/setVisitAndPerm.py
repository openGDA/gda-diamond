from copy import deepcopy

_setVisit = deepcopy(setVisit)
del setvisit

def setVisit(visit):
	_setVisit(visit)
	if not visit.startswith("cm"):
		i07userperm(visit)
	print("- Detector filepaths")
	print("pilatus1: {}".format(pil1.getFilePath()))
	print("pilatus2: {}".format(pil2.getFilePath()))
	print("pilatus3: {}".format(pil3.getFilePath()))
