from copy import deepcopy

_setVisit = deepcopy(setVisit)
del setvisit

def setVisit(visit):
	_setVisit(visit)
	if not visit.startswith("cm"):
		i07userperm(visit)
