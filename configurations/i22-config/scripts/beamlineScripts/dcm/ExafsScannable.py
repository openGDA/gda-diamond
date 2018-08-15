import java
import gda.device.scannable.ScannableBase
from math import log


class ExafsScannable(gda.device.scannable.PseudoDevice):
	"""
		Purpose:       A pseudo device for Exafs measurements
    		Author:        Tobias Richter
    		Date:          Feb 27 2008

    		This dummy scannable acts like a motor might, except rather than moving a physical axis, it simply moves an internal variable called currentPosition.

    		To use this script first run the script with the run button then in the Jython Terminal type exafssample = ExafsScannable("exafssample", d4diode1, s4xplusi)
    		where d4diode1 and sx4plusi are the diodes you are using for io and it respectively. These can be set differently if you like.
	"""

	def __init__(self, name, i0, it):
		""" Constructor takes a string as a name and i0 and it scannables """
		self.name = name
		self.setInputNames([name])
		self.i0 = i0
		self.it = it

	def isBusy(self):
		""" This dummy device is never busy"""
		return 0

	def getPosition(self):
		""" Return the exafs value"""
		return -log(self.it.getPosition()/self.i0.getPosition())

	def asynchronousMoveTo(self,newPosition):
		""" we are not moveable """
		return
