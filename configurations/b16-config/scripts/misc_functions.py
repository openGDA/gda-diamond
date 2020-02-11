from gda.device.scannable import PseudoDevice, ScannableBase
from gda.epics import CAClient

from gda.jython import InterfaceProvider
import os


def list_scannables():
	print "typed_name\tname\tclass\tmodule\tinput_fields\textra_fields"
	keys = globals().keys()
	keys.sort()
	for name in keys:
		obj = globals()[name]
		if isinstance(obj, PseudoDevice) or isinstance(obj, ScannableBase):
			if obj.getName()!=name:
				objectname = obj.getName()
			else:
				objectname = " "
			try:
				module = str(obj.__class__.__module__)
			except AttributeError:
				module = " "
			print name+"\t"+objectname+"\t"+str(obj.__class__)+"\t"+module+"\t" +str(list(obj.getInputNames()))+"\t"+str(list(obj.getExtraNames()))
			
	

def frange(start,end,step):
	'Floating-point version of range():   frange(start,end,step)'
	start=float(start); end=float(end); step=float(step);
	r=abs(end-start)
	step=abs(step)*(end-start)/r
	if abs(r/step)>1e6:
		print 'Too many points in list!'
		raise
	out=[start]
	while (abs(out[-1]-start)-abs(step/1e6))<r:
		out+=[out[-1]+step]
	return out[:-1]

def listprint(list):
	'Vertical print of list elements'
	for thing in list:
		print thing

def attributes(object):
	'Print top-level attributes of an object'
	attribs=dir(object)
	for attrib in attribs:
		print  attrib, '\t\t\t', eval('object.'+attrib)

#def help(object):
#	'Prints help for object'
#	print object.__doc__
	
#class helpClass:
#	'Gives help based on __.doc__ attribute'
#	def __init__(self,help_string):
#		self.help_string=help_string
#	def __call__(self, object_for_help):
#		print object_for_help.__doc__
#	def __repr__(self):
#		print "Type 'help object' to get help on object"
#		return self.help_string

#help=helpClass('I16 help system\nEmergency contact: 2222\nEHC contact 8571\nFor assistance call your local contact then EHC\nUse up/down arrow for previous commands\nCtrl+space\n')
#alias('help')

#def caget(pvstring):
#	cli=CAClient(pvstring)
#	cli.configure()
#	out=cli.caget()
#	cli.clearup()
#	return out

#def caput(pvstring,value):
#	cli=CAClient(pvstring)
#	cli.configure()
#	cli.caput(value)
#	cli.clearup()
	
def caget(pvstring):
	cli=CAClient(pvstring)
	if not cli.isConfigured():
		cli.configure()
	out=cli.caget()
#clearup is optional now
#	cli.clearup()
	return out

def caput(pvstring,value):
	cli=CAClient(pvstring)
	if not cli.isConfigured():
		cli.configure()
	cli.caput(value)
#	cli.clearup()

def cagetArray(pvstring):
	cli=CAClient(pvstring)
	if not cli.isConfigured():
		cli.configure()
	out=cli.cagetArray()
# 	cli.clearup()

def add(*items):
	#add  list objects containing lists of lists and numbers. arrays must be same size or scalar
	allscalars=1; somescalars=0; listsize=1; newitems=[];
	for item in items:
		newitems+=[item]				#add item to newitems list
		if isinstance(item,(int, float)):		#numerical objects
			somescalars=1;
		else:
			if len(item)==1:
				newitems[-1]=item[0];		#convert single element list to component object and replace last element in newitems list
				somescalars=1;
			else:
				allscalars=0;			#not all scalars
				if listsize==1:
					listsize=len(item);
				if listsize!=len(item):
					print "=== Inconsistent shape"
					raise
	if allscalars==1:					#all scalars so add
		tot=0;
		for item in newitems:
			tot=tot+item				#add as scalars
		return tot
	if somescalars==1:
		for i in range(len(newitems)):
			try:
				len(newitems[i]);		#will fail if not item with length
			except:
				newitems[i]=[newitems[i]]*listsize;	#pad out scalars to fit lists e.g. 1=>[1,1,1]
	result=(newitems[0])[:];					#remove bracket after bug fix? use [:] to avoid copy by reference
	for i in range(len(result)):
		for item in newitems[1:]:
			result[i]=add(result[i], item[i]);		#call add recursively if still not scalars
	return result

def mult(*items):
	#multiply list objects containing lists of lists and numbers. arrays must be same size or scalar
	#same as add but tot=1 and multiply scalars
	allscalars=1; somescalars=0; listsize=1; newitems=[];
	for item in items:
		newitems+=[item]				#add item to newitems list
		if isinstance(item,(int, float)):		#numerical objects
			somescalars=1;
		else:
			if len(item)==1:
				newitems[-1]=item[0];		#convert single element list to component object and replace last element in newitems list
				somescalars=1;
			else:
				allscalars=0;			#not all scalars
				if listsize==1:
					listsize=len(item);
				if listsize!=len(item):
					print "=== Inconsistent shape"
					raise
	if allscalars==1:					#all scalars so add
		tot=1;
		for item in newitems:
			tot=tot*item				#add as scalars
		return tot
	if somescalars==1:
		for i in range(len(newitems)):
			try:
				len(newitems[i]);		#will fail if not item with length
			except:
				newitems[i]=[newitems[i]]*listsize;	#pad out scalars to fit lists e.g. 1=>[1,1,1]
	result=(newitems[0])[:];					#remove bracket after bug fix? use [:] to avoid copy by reference
	for i in range(len(result)):
		for item in newitems[1:]:
			result[i]=mult(result[i], item[i]);		#call add recursively if still not scalars
	return result

class tracker():
	'''
	tracks slow variation of values of scalar or list of scalars
	tracker value is updated by adding in a small weight of the last value added
	weight=1.0 uses only the last value, 0.1 taked 0.1 weight of the last value etc
	default weight is 0.2
	e.g. 	tr=tracker(weight=0.1); 	#a new tracker
		tr=tracker(); 		#a new tracker (defaul weight)
		tr.add(hkl())		#add in small weight from current hkl
		print tr 			#display last added and next to use value
		pos hkl tr()		#move to tracker (weighted) value
	'''
	def __init__(self, weight=0.1):
		self.weight=weight
		self.nvals=0

	def __call__(self):
		assert self.nvals>0, "No values added to tracker yet"
		return self.trackerval
	
	def add(self, nextval):
		self.nextval=nextval
		if self.nvals==0:	#use just this value  as there are no previous ones
			self.trackerval=nextval
		else:	#weighted combination of this value and previous ones
			#self.trackerval=(1-self.weight)*self.trackerval+self.weight*nextval
			#this form uses add and mult functions to allow for lists
			self.trackerval=add(mult(add(1.0,mult(-1.0,self.weight)),self.trackerval),mult(self.weight,nextval))
		self.nvals+=1
	def __repr__(self):
		if self.nvals>0:
			return '=== Last value added: '+str(self.nextval)+'\n=== Next value to use:'+ str(self())
		else:
			return '=== tracker has been given no values yet'

def createVisitSubDir(subdir):
	"""
	Create a subdirectory (including parents) within the current visit
	Args:
		subdir (string): name of subdirectory e.g. 'detector1' or 'sample1/condition4'
	"""
	pathToCreate = InterfaceProvider.getPathConstructor().getVisitSubdirectory(subdir)
	if not os.path.exists(pathToCreate):
		try:
			os.makedirs(pathToCreate)
			print("Created directory: {}".format(pathToCreate))
		except:
			print("Could not create directory: {}".format(pathToCreate))
	else:
		print("Directory already exists: {}".format(pathToCreate))

