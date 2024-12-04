'''
Created on 27 Nov 2024

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase

XAS_MODES = ['TEY', 'TFY_ft', 'TFY_fb', 'TFY_90', 'PEY', 'PFY']

class XASMode(ScannableMotionBase):
    '''
    Scannable that allows to set XAS measurement mode - i.e. the default measurement PV or channel for the absorbed beam defined in NXxas.nxdl.xml 
    '''

    def __init__(self, name, mode = 'TEY'):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.mode = mode

    def getPosition(self):
        return self.mode

    def asynchronousMoveTo(self, m):
        if m not in XAS_MODES:
            raise ValueError("%s is not a supported measurement mode. Supported mode must be one of %r." % (m, XAS_MODES))
        self.mode = m

    def isBusy(self):
        return False


class XASModePathMapper(ScannableMotionBase):
    def __init__(self, name, mode, dic):
        self.setName(name)
        self.setInputNames([name])
        self.dict = dic
        self.mode = mode

    def getPosition(self):
        return self.dict[self.mode.getPosition()]

    def asynchronousMoveTo(self, pos):
        raise RuntimeError(self.getName() + " is a READ-ONLY scannable object")

    def isBusy(self):
        return False



