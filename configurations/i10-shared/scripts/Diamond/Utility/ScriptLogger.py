from org.slf4j import LoggerFactory
import traceback as traceback_mod;
from gdascripts.messages.handle_messages import getCauseList
from gda.jython import InterfaceProvider;



class SinglePrint(object):
	msg = None;
	
	@classmethod
	def sprint(self, msg):
		if msg != SinglePrint.msg:
			SinglePrint.msg = msg;
			print msg;
		return;
			

class Singleton(type):
	def __init__(self, name, bases, dict):
		super(Singleton, self).__init__(name, bases, dict)
		self.instance = None

	def __call__(self, *args, **kw):
		if self.instance is None:
			self.instance = super(Singleton, self).__call__(*args, **kw)
		return self.instance

class MyClass(object):
	__metaclass__ = Singleton

print(MyClass())


class ScriptLoggerClass(object):
	__metaclass__ = Singleton;
	singleMessage = None;
	
	def __init__(self):
		self.logger = LoggerFactory.getLogger("ScriptLogger");
		
	@classmethod
	def singlePrint(self, msg):
		if ScriptLoggerClass.singleMessage != msg:
			ScriptLoggerClass.singleMessage = msg;
			print(msg)
		return;
		
		
	def fullLog(self, controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False):
		msg = self.createMessage(msg, exceptionType, exception, traceback);
		if controller != None:
			controller.update(None, msg);
		if exception != None:
			self.logger.error(msg);
		else:
			self.logger.info(msg);
			
		InterfaceProvider.getTerminalPrinter().print(msg);
		if Raise:
			if isinstance(msg, Exception):
				raise msg;
			raise Exception(msg);
	
	def simpleLog(self, msg):
		self.fullLog(None, msg);
	
	def getCauseList(self, exception):
		return getCauseList(exception)
		
	def createMessage(self, msg, exceptionType=None, exception=None, traceback=None ):
		msg = self.spacer(msg);
			
		if exceptionType != None:
			msg = self.spacer(msg) + str(exceptionType);
		if exception != None:
			msg = self.spacer(msg) + self.getCauseList(exception);
		if traceback != None:
			msg = self.spacer(msg) + ".\n Stack follows: " + traceback_mod.format_exc();
		return msg;

	def spacer(self, msg):
		if msg is None:
			msg = "";
		elif msg != "":
			msg += " ";

		return msg;

#Usage:
#from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
#logger=ScriptLoggerClass();
