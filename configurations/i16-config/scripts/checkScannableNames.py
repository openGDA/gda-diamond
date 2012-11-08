print "The following scannables have labels (for typing) different than names(that go into files)"
print "Label\tName"
for label in dir():
	if (isinstance(eval(label),Scannable)):
		name = eval(label).getName()
		if label!=name:
			print label + "\t : " + name

lookupLabel={}
for label in filter( lambda label : isinstance(eval(label),Scannable) , dir() ):
	lookupLabel[eval(label).getName()]=label
