#!/bin/env python2.4

"Channel Access Example"

# load correct version of catools
import sys
from pkg_resources import require
require("dls.ca2==2.16")
from dls.ca2.catools import *

pv=sys.argv[1]
val=sys.argv[2]

caput( pv, [[ord(s) for s in val+"\0"]] )
result=str.join("",[chr(x) for x in caget(pv).dbr.value]).strip("\0")
print result
