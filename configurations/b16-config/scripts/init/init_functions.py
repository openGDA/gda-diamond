import math
from pprint import pprint

print "pdir(object) - pretty print object attributes"
def pdir(name):
	pprint(dir(name))

print "plist(list)  - pretty print a list, or other container"
def plist(list):
	for item in list:
		pprint(item)


print "datadir        - gets the current data directory"
print "datadir 'newpath' - changes the current data directory"

def frange(limit1, limit2, increment):
	"""Range function that accepts floats (and integers).
	"""
#		limit1 = float(limit1)
#		limit2 = float(limit2)
	increment = float(increment)
	count = int(math.ceil((limit2 - limit1) / increment))
	result = []
	for n in range(count):
		result.append(limit1 + n * increment)
	return result