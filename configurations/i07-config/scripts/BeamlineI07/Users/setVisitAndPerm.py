from copy import deepcopy

_setVisit = deepcopy(setVisit)
del setvisit

def setVisit(visit):
	_setVisit(visit)
	i07userperm(visit)
	setDir("")
