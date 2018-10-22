from Diamond.PseudoDevices.DeviceFunction import DeviceFunctionClass

print "-"*100
print "To create objects: idio and ifio";

idio = DeviceFunctionClass("idio", "ca61sr","ca62sr", "testFun");
ifio = DeviceFunctionClass("ifio", "ca63sr","ca62sr", "testFun");
ifioft = DeviceFunctionClass("ifioft", "ca64sr","ca62sr", "testFun");
ifiofb = DeviceFunctionClass("ifiofb", "ca65sr","ca62sr", "testFun");

def testFun(z, x):
	y=z/(x+1);
	return y;
