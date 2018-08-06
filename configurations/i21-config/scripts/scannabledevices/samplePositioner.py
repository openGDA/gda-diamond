'''
Created on 29 Aug 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
import math

class SamplePositioner(ScannableBase):
    '''
    classdocs
    '''
    POSITIONS=['Screws', 'Transfer', 'RIXS']

    def __init__(self, name, xpos,ypos,zpos,polarpos,tiltpos,azimpos,m5rotpos,diodetthpos, \
                 sax,say,saz,sapolar,satilt, saazim,m5tth,diodetth, \
                 xval,yval,zval,polarval,tiltval,azimval,m5rotval,diodetthval, \
                 tolerance=0.001):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.xpos=[xpos,sax,xval]
        self.ypos=[ypos,say,yval]
        self.zpos=[zpos,saz,zval]
        self.polarpos=[polarpos,sapolar,polarval]
        self.tiltpos=[tiltpos,satilt,tiltval]
        self.azimpos=[azimpos,saazim,azimval]
        self.m5rotpos=[m5rotpos,m5tth,m5rotval]
        self.diodetthpos=[diodetthpos,diodetth,diodetthval]
        self.tolerance=tolerance
        self.currentPosition=SamplePositioner.POSITIONS[2]
        
    def asynchronousMoveTo(self, posi):
        if str(posi) in SamplePositioner.POSITIONS:
            self.xpos[0].asynchronousMoveTo(str(posi))
            self.ypos[0].asynchronousMoveTo(str(posi))
            self.zpos[0].asynchronousMoveTo(str(posi))
            self.polarpos[0].asynchronousMoveTo(str(posi))
            self.tiltpos[0].asynchronousMoveTo(str(posi))
            self.azimpos[0].asynchronousMoveTo(str(posi))
            self.m5rotpos[0].asynchronousMoveTo(str(posi))
            self.diodetthpos[0].asynchronousMoveTo(str(posi))
        else:
            msg="Position '%s' is not supported." % (str(posi))
            raise Exception(msg)
        self.currentPosition=str(posi)
            
    def getPosition(self):
        inPos=True;
        msg=""
        if math.abs(float(self.xpos[2].getPosition()-float(self.xpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.xpos[0].getName())
            inPos=False
        if math.abs(float(self.ypos[2].getPosition()-float(self.ypos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.ypos[0].getName())
            inPos=False
        if math.abs(float(self.zpos[2].getPosition()-float(self.zpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.zpos[0].getName())
            inPos=False
        if math.abs(float(self.polarpos[2].getPosition()-float(self.polarpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.polarpos[0].getName())
            inPos=False
        if math.abs(float(self.tiltpos[2].getPosition()-float(self.tiltpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.tiltpos[0].getName())
            inPos=False
        if math.abs(float(self.azimpos[2].getPosition()-float(self.azimpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.azimpos[0].getName())
            inPos=False
        if math.abs(float(self.m5rotpos[2].getPosition()-float(self.m5rotpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.m5rotpos[0].getName())
            inPos=False
        if math.abs(float(self.diodetthpos[2].getPosition()-float(self.diodetthpos[1].getPosition())))>self.tolerance:
            msg+="%s: is not in position !\n" % (self.diodetthpos[0].getName())
            inPos=False
        if inPos:
            return self.currentPosition
        else:
            raise Exception(msg)
        
    def isBusy(self):
        return self.xpos[0].isBusy() or self.ypos[0].isBusy() or self.zpos[0].isBusy() or self.polarpos[0].isBusy() or \
         self.tiltpos[0].isBusy() or  self.azimpos[0].isBusy() or self.m5rotpos[0].isBusy() or  self.diodetthpos[0].isBusy()