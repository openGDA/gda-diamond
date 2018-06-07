from gda.jython.commands.ScannableCommands import pos

class PositionWrapper(object):
    def __init__(self, scannables):
        self.scannables = scannables
    def __call__(self):
        for scannable in self.scannables:
            print pos(scannable)
        
