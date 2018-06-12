# Convenience functions to set the offset of interferometer motors relative to relative to corresponding stage1 motors
# See also interferometer.xml
from gda.factory import Finder

def set_ifsy_offset(offset):
    Finder.getInstance().find('ifsy_offset').setOffset(offset)

def set_ifsz_offset(offset):
    Finder.getInstance().find('ifsz_offset').setOffset(offset)