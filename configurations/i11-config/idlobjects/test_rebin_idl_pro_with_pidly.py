#!/bin/env /dls/i11/software/python/bin/python

import pidly
idl = pidly.IDL()

#idl.pro('.compile /dls/i11/software/gda/config/idlobjects/testpy.pro')
idl.pro('.compile /dls/i11/software/gda/config/idlobjects/rebin_idl.pro')
idl.pro('rebin_idl',"-a"," 19423","/dls/i11/data/2010/ee0/"," 0.001","fin","ret")
#idl.pro('testpy',"qerty")
#print idl.x

#idl.close()

