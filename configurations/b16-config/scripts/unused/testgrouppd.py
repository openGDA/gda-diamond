import gdajython.devices.grouppdbase
reload(gdajython.devices.grouppdbase)

# Uses these DOFwrappers: dPhi,dChi,dTheta



#s=raw_input('okay?')
#print 'aaaa'
#print s


tmp = gdajython.devices.grouppdbase.GroupPDWithMemoryBase('tmpy',['phi','chi','eta'], [dPhi,dChi,dTheta], [.1,.2,.3])

tmp.displayConfiguration()