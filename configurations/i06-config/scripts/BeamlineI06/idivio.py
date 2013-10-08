
print "To create the idio and ifio";

idio = DeviceFunctionClass("idio", "ca61sr","ca62sr", "testFun1");

def testFun1(ca61sr, ca62sr):
	y=ca61sr/(ca62sr+1);
	return y;

ifio = DeviceFunctionClass("ifio", "ca63sr","ca62sr", "testFun2");

def testFun2(ca63sr, ca62sr):
	y=ca63sr/(ca62sr+1);
	return y;
