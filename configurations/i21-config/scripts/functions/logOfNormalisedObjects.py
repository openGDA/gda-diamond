from functions.device_function_class import DeviceFunctionClass
from math import log

def testFun(x1, x2):
	y=log(x1/x2);
	return y;

#Example: log(Im/I0)
#logratio = DeviceFunctionClass("ratio", "Im","I0", "testFun");
