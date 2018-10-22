from Diamond.Objects.EpicsPv import EpicsButtonClass
from Diamond.Objects.EpicsPv import EpicsPvClass

from gda.epics import CAClient;

from time import sleep;


import new, inspect;

class EpicsDeviceClass(object):
	
	#add a method to the class
	def add_method0(self, method, name=None):
		if name is None:
			name = method.func_name
		setattr(self.__class__, name, method)

		#add a method to the instance
	def add_method1(self, method, name=None):
		if name is None:
			name = method.func_name
		nm=new.instancemethod(method, self, self.__class__)
		setattr(self, name, nm)

	def funToBeAdded(self, baseClass):
		i=inspect.stack();
		print i;
		import dis;
		dis.dis(self);
		print type(self);
		print type(baseClass);
		return;
	
	def selfadd(self):
		self.add_method1(self.funToBeAdded, "f4");
	
	
	
def newfun(self):
	return "I am a new function";

def newnewfun(self, name):
	return "I am " + name;

o = EpicsDeviceClass()

print dir(o)
o.add_method0(newfun, "f1")
o.add_method1(newfun, "f2")
o.add_method1(newnewfun, "f3")
o.selfadd();

print dir(o)
o.f1()
o.f2()
