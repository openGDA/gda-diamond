# Convenience functions to set the offset of interferometer motors relative to relative to corresponding stage1 motors
# See also interferometer.xml
from gda.factory import Finder
from gda.jython.commands.GeneralCommands import alias

def set_ifsy_offset(offset):
    Finder.find('ifsy_offset').setOffset(offset)

def get_ifsy_offset():
    return Finder.find('ifsy_offset').getOffset()

def set_ifsz_offset(offset):
    Finder.find('ifsz_offset').setOffset(offset)

def get_ifsz_offset():
    return Finder.find('ifsz_offset').getOffset()

def get_ifs_offsets():
    print('ifsy_offset: ' + str(get_ifsy_offset()))
    print('ifsz_offset: ' + str(get_ifsz_offset()))

alias('get_ifsy_offset')
alias('get_ifsz_offset')
alias('get_ifs_offsets')
