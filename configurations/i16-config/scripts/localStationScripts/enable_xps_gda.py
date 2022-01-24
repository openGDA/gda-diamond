import os
class enable_xps_with_python_script:
	'''
	Enables all XPS axes if called with no args and no ()
	Else enables specified axis number if called as a function with()
	'''
	def __init__(self,commandstring,maxaxis):
		self.commandstring=commandstring
		self.maxaxis=maxaxis

	def enable(self,axis):
		self.command=self.commandstring+' '+str(axis)
		self.fi,self.fo,self.fe=os.popen3(self.command)
		self.output=self.fo.readlines()
		self.errors=self.fe.readlines()
		print self.list_of_strings_to_string(self.output+self.errors)

	def list_of_strings_to_string(self, listofstrings):
		stringout=''
		for thing in listofstrings:
			stringout+=thing
		return stringout


	def __call__(self, axis):
		if axis>1 and axis<self.maxaxis:
			self.enable(axis)
		else:
			print "=== error in axis number"

	def __repr__(self):
		print "=== Enabling all XPS axes - will return Error -22 if already enabled (this is OK)"
		for i in range(self.maxaxis):
			self.enable(i+1)
		return "=== Done"

enablexps=enable_xps_with_python_script('python /dls_sw/prod/R3.14.11/ioc/BL16I/BL/3-21/data/enable_xps.py',6)
