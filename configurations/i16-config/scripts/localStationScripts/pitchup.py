from gda.epics import CAClient

class pitchupClass:
	'''
	Experimental class to use qbpm to tweek finepitch 
	Use with care
	'''
	def __call__(self):
		self.in6=qbpm6inserter()
		self.finepitch=finepitch()
		self.ic1=ic1()
		self.at=atten()[0]
	
		if self.ic1>0.1:
			qbpm6inserter(1)
			atten(0)
			sleep(1.5)
			print vpos, finepitch, ic1
			inc((finepitch, -vpos()/.031))
			sleep(1.5)
			print vpos, finepitch, ic1
			inc((finepitch, -vpos()/.031))
			sleep(1.5)
			print vpos, finepitch, ic1
		else:
			print '=== IC1 signal too weak for pitchup - no adjustment'
			atten(self.at)
			qbpm6inserter(self.in6)
			return

		if ic1()<0.75*self.ic1:
			print '=== IC1 signal seems to have gone down - going back to original finepitch'
			print finepitch(self.finepitch)
		atten(self.at)
		qbpm6inserter(self.in6)


