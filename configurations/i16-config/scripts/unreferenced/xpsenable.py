import os

def xpsenable():
	tmp = os.popen('python /dls_sw/i16/software/gda/config/pythonscripts/i16xpsenable.py').readlines()
	return '\n'.join(tmp)

def xpsdisable():
	tmp = os.popen('python /dls_sw/i16/software/gda/config/pythonscripts/i16xpsdisable.py').readlines()
	return '\n'.join(tmp)
