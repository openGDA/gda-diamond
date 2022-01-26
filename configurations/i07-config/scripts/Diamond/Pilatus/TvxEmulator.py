"""
Classes and methods to emulate commonly-used TVX image processing commands in GDA.

TVX Commands to implement, not yet done

"""

class GdaTvx:
	
	def mkmask(self):
		"""
		mkmask help.
		"""
		print "GdaTvx makemsk"
		
	def maskimg(self):
		"""
		maskimg help.
		"""
		print "GdaTvx mskimg"
		
		
		
def testGdaTvx():
	gdatvx = GdaTvx()	
	print "gdatvx: " + str(gdatvx)
	
	
if __name__ == '__main__':
	testGdaTvx()