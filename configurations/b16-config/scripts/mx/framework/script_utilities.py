''' Module that facilitates management and interrogation of script state '''

import java.lang.Exception
import sys
import time

from java.lang import IllegalAccessError

from gdaserver import commandQueueProcessor # @UnresolvedImport
from gda.commandqueue import JythonCommandCommandProvider
from gdascripts.messages import handle_messages
from gda.jython import JythonServerFacade, JythonStatus
from gda.jython.commands.InputCommands import requestInput
from gda.jython.scriptcontroller import ScriptEvent
from gda.factory import Finder
from java.util.function import Predicate

from org.slf4j import LoggerFactory

logger = LoggerFactory.getLogger(__name__)

def checkTolerance(a, b, tolerance=0.0):
	return abs(a - b) <= tolerance


def confirm(question, options_key = '[yn]', expected='y', use_logger=None):
	''' Confirm returns True if the answer is the same as expected, otherwise false '''
	show_question = str(question).strip() + ' ' + options_key + ': '
	answer = requestInput(show_question)
	
	if use_logger:
		use_logger.debug('Confirm: {}', show_question)
		use_logger.debug('Response: {}', answer)
	
	return answer == expected


def dateAndTime():
	return time.asctime(time.localtime())


def device(name):
	return Finder.find(name)


def enqueueCommandString(command_string, description="script", settings_path=None):
	provider = JythonCommandCommandProvider(command_string, description, settings_path)
	return enqueueProvider(provider)


def enqueueProcedure(procedure):
	return enqueueCommandString(procedure.getScript(), procedure.getDescription(), None)


def enqueueProvider(provider):
	command_id = commandQueueProcessor.addToTail(provider)
	logger.debug("Enqueued: %s" % provider.getCommand().getDescription())
	return command_id


def enqueueScriptController(controller):
	return enqueueCommandString(controller.getCommand(), controller.getCommand())


def getScanStatus():
	return JythonServerFacade.getInstance().getScanStatus()


def getScriptStatus():
	return JythonServerFacade.getInstance().getScriptStatus()


def isScanIdle():
	return JythonStatus.IDLE == getScanStatus()


def isScriptIdle():
	return JythonStatus.IDLE == getScriptStatus()


def not_implemented(note=None):
	message = "Functionality not implemented"
	if note:
		message = "%s : %s" % (message, note)
	raise IllegalAccessError(message)


def update(controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False, logger_ref=logger):
	
	if isinstance(exceptionType, ScriptBaseInterruption):
		traceback = None
	
	if isinstance(exception, ScriptBaseInterruption):
		traceback = None
	
	message = msg # default
	if controller != None and Raise: # On Raise=True, ensure ScriptEvent propagated
		message = ScriptEvent(None, ScriptEvent.Event.Exception, msg) # @UndefinedVariable
	
	handle_messages.log(controller, message, exceptionType, exception, traceback, Raise, logger_ref)


def userlog(message, logger_ref=logger, level='info'):
	''' Log and show on user console '''
	if logger_ref:
		if level == 'info':
			logger_ref.info(message)
		elif level == 'debug':
			logger_ref.debug(message)
		elif level == 'error':
			logger_ref.error(message)
		else:
			logger_ref.warn(message)
	
	print (message)


def validate(test_expression, fail_msg, do_raise=True, script_controller=None, logger=None):
	if not test_expression:
		handle_messages.log(script_controller, fail_msg,
			ValueError if do_raise else None,
			ValueError(fail_msg) if do_raise else None,
			traceback=None, Raise=do_raise, logger=logger)
	
	return test_expression


class Aborted(Exception):
	pass


class ScriptBaseInterruption(ScriptEvent):
	
	DEFAULT_MESSAGE = "Script interrupted by the user"
	
	def __init__(self, reason=DEFAULT_MESSAGE):
		super(None,ScriptEvent.Event.Exception,reason) # @UndefinedVariable

	def getMessage(self):
		return self.getExceptionString()


class UserRequestedHaltException(java.lang.Exception):
	
	DEFAULT_MESSAGE = "Script interrupted by the user"
	
	def __init__(self,reason=DEFAULT_MESSAGE):
		self.reason = reason

class LambdaWrapper(Predicate):
	def __init__(self, fn):
		self.test = fn