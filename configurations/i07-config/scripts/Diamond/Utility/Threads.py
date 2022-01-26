
from java import lang


#    Java thread body
class BackgroundRunningTask(lang.Thread):
    def __init__ (self, runner, param=None):
        self.__runner = runner   # function to run
        self.__param = param     # function parameter (if any)
        self.complete = 0
        self.running = 0

    def run (self):
        self.complete = 0;
        self.running = 1
        
        if self.__param is not None: 
            self.result = self.__runner(self.__param)
        else:
            self.result = self.__runner()
            
        self.complete = 1; self.running = 0

#To start a long running activity
def doAsync (func, param):
    BackgroundRunningTask(func, param).start()

