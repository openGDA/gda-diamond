from threading import Thread
import sys

class ScriptThread(Thread):
	
	def __init__(self):
		Thread.__init__(self)
		self.exception = None

# http://softwareramblings.com/2008/06/running-functions-as-threads-in-python.html
class FunctionThread(ScriptThread):
	
	def __init__(self, target, *args):
		ScriptThread.__init__(self)
		self.target = target
		self.args = args
	
	def run(self):
		try:
			self.target(*self.args)
		except:
			self.exception = sys.exc_info()[1]

def start_threads(*threads):
	"""Starts all the specified threads"""
	for t in threads:
		t.start()

def wait_for_threads_to_complete(*threads):
	"""Waits for all the specified threads to complete. Will not return until they have all completed"""
	for t in threads:
		t.join()

def one_or_more_failed(*threads):
	"""Checks whether any of the threads failed"""
	for t in threads:
		if t.exception:
			return True
	return False

def reraise_any_thread_exceptions(*threads):
	"""Re-raises any exception generated while the specified threads were running"""
	for t in threads:
		if t.exception:
			raise t.exception
