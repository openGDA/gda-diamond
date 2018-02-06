#!/bin/env /dls/i11/software/python/bin/python

import pidly
idl = pidly.IDL()

idl.pro('.compile /dls/i11/software/gda/config/idlobjects/testpy.pro')
idl.pro('testpy', 30)
#print idl.x

idl.close()
