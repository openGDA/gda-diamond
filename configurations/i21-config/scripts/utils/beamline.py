from gda.jython.commands.GeneralCommands import alias

from utils.BeamlineFunctions import BeamlineFunctionClass
from gda.configuration.properties import LocalProperties
print("-"*100)
print("create 'beamlinefunction' object and commands 'last_scan_file', 'get_title', 'set_title', 'get_visit', 'set_visit', 'set_directory', 'get_directory'")

beamline = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)
beamlinefunction = BeamlineFunctionClass(beamline);
beamlinefunction.set_terminal_logger();

def last_scan_file():
    return beamlinefunction.get_last_scan_file()

def set_title(title):
    beamlinefunction.set_title(title)
    
def get_title():
    return beamlinefunction.get_title()

def set_visit(visit):
    beamlinefunction.set_visit(visit)
    beamlinefunction.set_sub_dir("")

def get_visit():
    return beamlinefunction.get_visit()

def set_directory(new_sub_dir):
    beamlinefunction.set_sub_dir(new_sub_dir)
    
def get_directory():
    beamlinefunction.get_data_path()


alias("last_scan_file")
alias("set_title")
alias("get_title")
alias("get_visit")
alias("set_visit")
alias("set_directory")   
alias("get_directory")


