'''
Created on 1 Nov 2024

@author: fy65
'''

from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from time import sleep


class q_motion(ScannableBase):
    def __init__(self, name):
        self.setName(name)
        self.setOutputFormat(['%.2f'])
        self.currentPosition = 0.0
        self.setInputNames([name]);
        self._isbusy = False
        self.xoffset = 0.0
        self.yoffset = 0.0

    def isBusy(self):
        return self._isbusy

    def getPosition(self):
        return self.currentPosition
    def asynchronousMoveTo(self,new_position):
        self._isbusy = True
        print('-> new angle = ', new_position)
        move_ill(new_position, self.xoffset, self.yoffset)
        self.currentPosition=new_position
        self._isbusy = False


class LeemModule(ScannableBase):
    def __init__(self, name,module):
        self.name = name
        self.setOutputFormat(['%.2f'])
        self.currentPosition = 0.0
        self.setInputNames(['mA']);
        self.module = module
        self._isbusy = False
       
        pvOut = 'BL06K-EA-LEEM-01:PS'
        self.chOut=CAClient(pvOut)
        self.chOut.configure()
       
        pvChannel = 'BL06K-EA-LEEM-01:PS:INDEX'
        self.pvChannel=CAClient(pvChannel)
        self.pvChannel.configure()
       
    def isBusy(self):
        return self._isbusy

    def getPosition(self):
        return self.currentPosition

    def asynchronousMoveTo(self,new_position):
        self._isbusy = True
        self.pvChannel.caput(self.module)
        sleep(0.25)
        self.chOut.caput(new_position)
        self.currentPosition=new_position
        self._isbusy =  False

from cmath import sin, cos, pi

exec("[illx, illy] = [None, None]")
illx = LeemModule('illx', 30)
illy = LeemModule('illy', 31)

def ill(posx, posy):
    illx.moveTo(posx)
    illy.moveTo(posy)


def q_coord(angles, xoffset=0, yoffset=0):
    rotEllCoeff = [2.4541,45.0491,-0.01,-0.1068,-0.0026]
    x = xoffset+rotEllCoeff[0]*cos(angles)*cos(rotEllCoeff[4]) - rotEllCoeff[1]*sin(angles)*sin(rotEllCoeff[4])+rotEllCoeff[2]
    y = yoffset+rotEllCoeff[0]*cos(angles)*sin(rotEllCoeff[4]) - rotEllCoeff[1]*sin(angles)*cos(rotEllCoeff[4])+rotEllCoeff[3]
    return [x.real, y.real]

def move_ill(angle,  xoffset=0, yoffset=0):
    rad  = angle*pi/180.0
    [leem_illx, leem_illy] = q_coord(rad)
    leem_illx += xoffset
    leem_illy += yoffset
    ill(leem_illx, leem_illy)

exec('[q_move]=[None]')
q_move = q_motion('q_move')
