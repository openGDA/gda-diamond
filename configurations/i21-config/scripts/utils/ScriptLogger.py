
from org.slf4j import LoggerFactory  # @UnresolvedImport
import traceback as traceback_mod
from gdascripts.messages.handle_messages import getCauseList

class SinglePrint(object):
	msg = None;
	
	@classmethod
	def sprint(cls, msg):
		if msg != SinglePrint.msg:
			SinglePrint.msg = msg
			print(msg)
			

class Singleton(type):
	def __init__(self, name, bases, dict1):
		super(Singleton, self).__init__(name, bases, dict1)
		self.instance = None

	def __call__(self, *args, **kw):
		if self.instance is None:
			self.instance = super(Singleton, self).__call__(*args, **kw)
		return self.instance


class ScriptLoggerClass(object):
	__metaclass__ = Singleton;
	single_message = None;
	
	def __init__(self):
		self.logger = LoggerFactory.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)
		
	@classmethod
	def singlePrint(cls, msg):
		if ScriptLoggerClass.single_message != msg:
			ScriptLoggerClass.single_message = msg
			print(msg)
	
	def dump(self, msg, exception_type=None, exception=None, traceback=None):
		msg = self.create_message(msg, exception_type, exception, traceback);
		print(msg);
		
	def log(self, controller, msg, exception_type=None, exception=None, traceback=None, re_raise=False):
		self.full_log(controller, msg, exception_type, exception, traceback, re_raise)
		
	def full_log(self, controller, msg, exception_type=None, exception=None, traceback=None, re_raise=False):
		shortmsg = self.create_message(msg, None, exception, None)
		msg = self.create_message(msg, exception_type, exception, traceback)
		if controller != None:
			controller.update(None, msg)
		if exception != None:
			self.logger.error(msg)
		else:
			self.logger.info(msg)			
		print(shortmsg)
		if re_raise:
			if isinstance(msg, Exception):
				raise msg
			raise Exception(msg)
	
	def simple_log(self, msg):
		self.full_log(None, msg);
	
	def get_cause_list(self, exception):
		return getCauseList(exception)

	def create_message(self, msg, exception_type=None, exception=None, traceback=None):
		msg = self.spacer(msg);
			
		if exception_type != None:
			msg = self.spacer(msg) + str(exception_type);
		if exception != None:
			msg = self.spacer(msg) + self.get_cause_list(exception);
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
