from gda.configuration.properties import LocalProperties
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names
from java.util.function import Predicate, Consumer  # @UnresolvedImport

print("Running k11_utilities.py")

def is_live():
    mode = LocalProperties.get("gda.mode")
    return mode =="live"

def ls_scannables():
    ls_names(Scannable)


class JPredicate(Predicate):
    """
    Jython wrapper for java.lang.function.Predicate.
    
    A simple lambda won't suffice because of default methods.
    Instead, construct an instance of this with your lambda.
    """
    def __init__(self, predicate):
        self.predicate = predicate
    
    def test(self, value):
        return self.predicate(value)
    
class JConsumer(Consumer):
    def __init__(self, consumer):
        self.consumer = consumer
    
    def accept(self, val):
        self.consumer(val)