#print "inside subprocess"


import sys, os
sys.path.append(os.path.dirname("/dls_sw/i10/scripts/"))

from zhinst import ziPython

print "after load zipython"

daq = ziPython.ziDAQServer('172.23.110.84', 8004)
sample = daq.getSample('/dev4206/demods/0/sample')
print sample



#print "end of subprocess"
