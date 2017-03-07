#from java import lang
from java.lang import System
from time import sleep
import math
from gda.device.scannable import PseudoDevice

class Stv_Obj(PseudoDevice):
    def __init__(self, name):
        self.name = name
        self.setOutputFormat(['%4.1f'])
        #self.currentPosition = leem.getPSValue(38)
        self.currentPosition = leem_stv.getPosition()
        self.setInputNames(['stv_obj']);
        
        self.a = -38.7462
        self.b = -12.82824
        self.c = 20.92462 
   
        #self.objStart = leem.getPSValue(11)-(self.a - self.b*math.log(leem.getPSValue(38) + self.c))
        self.objStart = leem_obj.getPosition()-(self.a - self.b*math.log(leem_stv.getPosition() + self.c))
        #print(self.objStart), leem_obj.getPosition(), leem_stv.getPosition()

    def isBusy(self):
        return False

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        #return leem.getPSValue(38)
        return leem_stv.getPosition()

 
    def asynchronousMoveTo(self,new_position):
        #self.objStart = leem.getPSValue(11)-(self.a - self.b*math.log(leem.getPSValue(38) + self.c))
        self.objStart = leem_obj.getPosition()-(self.a - self.b*math.log(leem_stv.getPosition() + self.c))
        #leem.setPSValue(38,new_position)
        leem_stv.asynchronousMoveTo(new_position)
        self.currentPosition=new_position
        #move the obj accordingly
        deltaObj = self.a - self.b*math.log(new_position + self.c)
        finalObj = self.objStart + deltaObj
        #leem.setPSValue(11,finalObj)
        leem_obj.asynchronousMoveTo(finalObj)
        return
 
exec('[stvobj] = [None]')
stvobj = Stv_Obj('stvobj')
