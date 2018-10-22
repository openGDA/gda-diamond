# To reloading all modules

#For dubugging an imported module, because the import statement check if the module is already in memory and do the import 
#only when this is mandated, The latest module is not loaded. This scripts is used to deal with this problem.


You can use the reload() function but this is quite difficult if you do changes in a module wich 
isn't directly imported by your test script.

A good solution could be to remove all modules from memory before running the test script. 
You only have to put some few lines at the start of your test script.
	Python

 1
 2
 3
 4
 5
 6
 7
 8
 9
10
11

	

#solution1:
import sys;

def cleanall():
	sys.modules.clear()

def reloadall():
	if globals().has_key('init_modules'):
		for m in [x for x in sys.modules.keys() if x not in init_modules]:
			del(sys.modules[m]) 
	else:
		init_modules = sys.modules.keys()

