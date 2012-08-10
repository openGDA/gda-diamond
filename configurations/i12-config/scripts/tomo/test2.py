from gda.observable import IObservable
from gda.observable import IObserver
#ref = refinement()
#ref.calibrateElement(20.0,0,23. 24. 22.4 0.001)

class test2(IObserver) :
 	def __init__(self):
 		pass
 	
 	def update(self, source, arg):
 		print `source`
 		print `arg`
 		pass

	