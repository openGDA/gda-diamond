#import os

#class display_data_file:
#	'''
#	Display a data file, specified by number, looking in datadir directory 
#	'''
#
#	def __init__(self,datadir_function,display_prog,file_startchar,file_ext):
#		self.datadir_function=datadir_function
#		self.display_prog=display_prog
#		self.file_startchar=file_startchar
#		self.file_ext=file_ext
#
#	def __call__(self, run_num):
#		self.dir=self.datadir_function()
#		self.filename=self.dir+'/'+self.file_startchar+str(run_num)+self.file_ext
#		self.command=self.display_prog+' '+'"'+self.filename+'"'
#		os.system(self.command)
#		print "=== Attempting to display "+self.filename+" in new window"
#	
#showdatfile=display_data_file(datadir,'less','','.dat')

