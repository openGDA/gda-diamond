#!/bin/env python2.6

#
# Command line app that sends things to the motoman
#  motoman.py -ip=<ipaddr> -cmd=<command> -dat=<data>
#

import os, sys, socket 
import time
from gdascripts.messages import handle_messages
import copy
import math
class Position():
    def __init__(self, X=0., Y=0.,Z=0.,RX=0.,RY=0.,RZ=0.):
        self.X=X
        self.Y=Y
        self.Z=Z
        self.RX=RX
        self.RY=RY
        self.RZ=RZ
        self.type="0"
        self.tool = "0"
        self.ext1=0.
        self.ext2=0.
        self.ext3=0.
        self.ext4=0.
        self.ext5=0.
        self.ext6=0.
        self.flip=False
        self.arm="Upper"
        self.side="Front"
        self.RLessThan180=True
        self.TLessThan180=True
        self.SLessThan180=True
        
        
    def asDataString(self):
        arg1 = "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f," %( self.X,self.Y,self.Z,self.RX,self.RY,self.RZ)
        arg2 = "%s,%s," %( self.type,self.tool)
        arg3 = "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f" %( self.ext1,self.ext2,self.ext3,self.ext4,self.ext5,self.ext6)
        return arg1+arg2+arg3
    def __repr__(self):
        return self.asDataString()
    
    def __sub__(self,other):
        res=self.getCopy()
        res.X -= other.X
        res.Y -= other.Y
        res.Z  -= other.Z
        res.RX -= other.RX
        res.RY -= other.RY
        res.RZ -= other.RZ
        return res

    def __add__(self,other):
        res=self.getCopy()
        res.X += other.X
        res.Y += other.Y
        res.Z  += other.Z
        res.RX += other.RX
        res.RY += other.RY
        res.RZ += other.RZ
        return res
    
    def getCopy(self):
        return copy.deepcopy(self)
    
    def __eq__(self,other):
        return self.withinResolution(other, res=0.)

    def __ne__(self,other):
        return not self.__eq__(other)
    
    def __getValueForMoveTowards(self,val, final, step, res ):
        diff = final-val
        absDiff= math.fabs(diff)
        if absDiff > res:
            absStep = math.fabs(step)
            if absDiff < absStep:
                return final

            if diff > 0:
                return val + absStep
            return val - absStep
        return final

    def moveTowards(self, final, steps, res=0.001):
        result=self.getCopy()
        result.X = self.__getValueForMoveTowards(result.X, final.X, steps.X, res)
        result.Y = self.__getValueForMoveTowards(result.Y, final.Y, steps.Y, res)
        result.Z = self.__getValueForMoveTowards(result.Z, final.Z, steps.Z, res)
        result.RX = self.__getValueForMoveTowards(result.RX, final.RX, steps.RX, res)
        result.RY = self.__getValueForMoveTowards(result.RY, final.RY, steps.RY, res)
        result.RZ = self.__getValueForMoveTowards(result.RZ, final.RZ, steps.RZ, res)
        return result
    
    def withinResolution(self,other,res=.001):
        return (math.fabs(self.X - other.X) <= res) and \
            (math.fabs(self.Y - other.Y) <= res) and \
            (math.fabs(self.Z - other.Z) <= res) and \
            (math.fabs(self.RX - other.RX) <= res) and \
            (math.fabs(self.RY - other.RY) <= res) and \
            (math.fabs(self.RZ - other.RZ) <= res) 
    
class Motoman(object):

    def __init__(self, ip, timeout=5, single_cmd_mode=True):
        self.ip = ip
        self.connected=False
        self.verbose=False
        self.timeout=timeout
        self.single_cmd_mode = single_cmd_mode

    def log(self,txt):
        handle_messages.log(None, txt)

    def connect(self):
        if self.connected:
            return
        self.motoman = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.motoman.settimeout(self.timeout)
        self.motoman.connect((self.ip, 80))
        if not self.single_cmd_mode:
            self.sendStartKeepAlive()
        self.connected=True
#        self.motoman.setblocking(True)

    def sendStartKeepAlive(self):
        reply = self.sendAndReceive( 'CONNECT Robot_access Keep-Alive:2.\r\n', '\r\n')
        expected_reply = "OK: DX Information Server( 1.16).\r\n"
        if reply != expected_reply:
            self.disconnect()
            raise Exception("Incorrect reply from command '%s'. Expected '%s' Actual '%s'" %( message_to_send, expected_reply, reply))
        
    def sendStart(self):
        reply = self.sendAndReceive( 'CONNECT Robot_access\r\n', '\r\n')
        expected_reply = "OK: DX Information Server( 1.16).\r\n"
        if reply != expected_reply:
            self.disconnect()
            raise Exception("Incorrect reply from command '%s'. Expected '%s' Actual '%s'" %( message_to_send, expected_reply, reply))

    def reconnect(self):
        self.disconnect()
        self.connect()

    def disconnect(self):
        if self.connected:
            self.motoman.close()
            self.motoman = None
            self.connected=False
        
    def checkConnected(self):
        if not self.connected:
            raise Exception("Not connected to " + `self.ip`)

    def sendAndReceive(self,text, term):
        self.checkConnected()
        self.log(  "Sent: %s"  % (text)) 
        sent = self.motoman.send(text)
        expected_sent = len(text)
        if sent != expected_sent:
            raise Exception ("Error sending command. Sent = %d Excepted = %d" % ( sent, expected_sent))
        return self.receive(term)

    def receive(self,  term):
        self.checkConnected()
        reply = self.motoman.recv(1024)
        self.log( "Recv: %s" %(reply))
        start_time = time.clock()
        while reply.find(term) == -1:
            time.sleep(.1)
            morereply = self.motoman.recv(1024)
            self.log( "Recv: %s" %(morereply))
            reply += morereply
            now = time.clock()
            if now-start_time > self.timeout:
                raise "Reply timeout reply so far %s" %(reply)
        return reply

    def readCurrentPositionInJointSpace(self):
        return self.doCommand("RPOSJ").strip()

    def readCurrentPositionInBaseSpaceWithExternalAxis(self):
        return self.doCommand("RPOSC","0,1").strip()

    def readCurrentPositionInRobotSpaceWithExternalAxis(self):
        return self.doCommand("RPOSC","1,1").strip()

    def readCurrentPositionInUser1SpaceWithExternalAxis(self):
        return self.doCommand("RPOSC","2,1").strip()
    
    def interpretAsBoolean(self,intAsString, bit ):
        b1=int(intAsString)
        return b1>>bit &0x1 == 1

    def interpretAsString(self, intAsString, bit, valFalse, valTrue):
        if self.interpretAsBoolean(intAsString, bit):
            return valTrue
        return valFalse
        
    def convertReplyToPosition(self, p):
        xyz= Position()
        xyz.X = float(p[0])
        xyz.Y = float(p[1])
        xyz.Z = float(p[2])
        xyz.RX = float(p[3])
        xyz.RY = float(p[4])
        xyz.RZ = float(p[5])
        
        type = p[6]
        xyz.type=type
        xyz.tool = p[7]
        xyz.ext1=float(p[8])
        xyz.ext2=float(p[9])
        xyz.ext3=float(p[10])
        xyz.ext4=float(p[11])
        xyz.ext5=float(p[12])
        xyz.ext6=float(p[13])
        xyz.flip=not self.interpretAsBoolean(type, 0)
        xyz.arm=self.interpretAsString(type,1, "Upper","Lower")
        xyz.side=self.interpretAsString(type,2,"Front", "Back")
        xyz.RLessThan180=not self.interpretAsBoolean(type, 3)
        xyz.TLessThan180=not self.interpretAsBoolean(type, 4)
        xyz.SLessThan180=not self.interpretAsBoolean(type, 5)
        return xyz

    
    def readRobotPositions(self):
        p = self.readCurrentPositionInRobotSpaceWithExternalAxis().split(",")
        return self.convertReplyToPosition(p)
    
    def makeEmptyPosition(self):
        return Position()

    def moveToPositionInRobotSpace(self, xyz=Position(), speed=5, doIt=True):
        arg = ""
        arg += `speed` +","
        arg += "0"  + ","# although this indicates Base it works with the values return by readRobotPositions
        xyz.type="0"
        arg += xyz.asDataString()
        self.log(arg)
        if doIt:
            switchServoOff=True
            try:
                stat=self.readStatus()
                if stat["alarm"] == "1":
                    raise Exception("Robot in alarm state before move")
                if stat["servo_on"] == "1":
                    switchServoOff = False
                else:
                    self.setServoOn()
                reply =  self.doCommand("MOVJ",arg)
                expected_reply = "0000\r\n"
                if not reply.startswith(expected_reply):
                    raise Exception("Incorrect reply Expected '%s' Actual '%s'" %( expected_reply, reply))

                self.waitForEndOfMove()

                    
            finally:
                if switchServoOff:
                    self.setServoOff()
        
    def waitForEndOfMove(self):    
        ##wait for move to stop
        stat=self.readStatus()
#        if stat["alarm"] :
#            raise Exception("Robot in alarm state")
        if stat["error"] :
            raise Exception("Robot in error state")
        ctr=0
        while stat["running"]:
            time.sleep(0.1)
            ctr += 1
            if ctr > 600:
                raise Exception("Move did not complete in time - 60s")
            stat=self.readStatus()
#            if stat["alarm"]:
#                raise Exception("Robot went into alarm state during move")
            if stat["error"] :
                raise Exception("Robot in error state")

    def resetAlarm(self):
        stat=self.readStatus()
        if stat["alarm"]:
            self.doCommand("RESET","")
            time.sleep(1.0)
            stat=self.readStatus()
            if stat["alarm"]:
                raise Exception("Robot in alarm state after reset")
        
    def moveIncrementalInRobotSpace(self, xyz=Position(), speed=5, doIt=True, userCoordinates=0):
        self.log("moveIncrementalInRobotSpacem called for xys=%s" %(xyz))
        arg = ""
        arg += "0" +"," #speed selection
        arg += `speed` +","
        arg += `userCoordinates`  + ","# although this indicates Base it works with the values return by readRobotPositions
        xyz.type="0"
        arg += xyz.asDataString()
        self.log(arg)
        if doIt:
            switchServoOff=True
            try:
                stat=self.readStatus()
#               if stat["alarm"]:
#                    raise Exception("Robot in alarm state before move")
                if stat["servo_on"]:
                    switchServoOff = False
                else:
                    self.setServoOn()
                print "IMOV %s" %(arg)
                reply =  self.doCommand("IMOV",arg)
                expected_reply = "0000\r\n"
                if not reply.startswith(expected_reply):
                    raise Exception("Incorrect reply Expected '%s' Actual '%s'" %( expected_reply, reply))
                self.waitForEndOfMove()
            except :
                exceptionType, exception, traceback = sys.exc_info()
                handle_messages.log(None, "Error in moveIncrementalInRobotSpace", exceptionType, exception, traceback, True)
                
            finally:
                if switchServoOff:
                    time.sleep(1.0)
                    self.setServoOff()

    def abort(self):
        self.abort=True
        
    def moveUsingIncrements(self, xyz_start=None, xyz_final=None, steps=None, res=0.001, speed=5, doIt=True, userCoordinates=0):
        self.setServoOn()
        try:
            self.abort = False
            prev_pos = xyz_start
            start_time=time.clock()
            while not prev_pos.withinResolution(xyz_final,res):
                now=time.clock()
                if now-start_time > 180:
                    raise Exception("Time to move > 180s")
                if self.abort:
                    raise Exception("Move aborted")
                next_pos = prev_pos.moveTowards(xyz_final, steps,res)
                self.log( "prev_pos = %s" %(prev_pos))
                self.log( "xyz_final = %s" %(xyz_final))
                self.log("next_pos = %s" %(next_pos))
                delta = next_pos - prev_pos
                self.log("delta = %s" %(delta))
                self.moveIncrementalInRobotSpace(delta, speed=speed, doIt=doIt, userCoordinates=userCoordinates)
                prev_pos = next_pos
                time.sleep(1)
        finally:
            self.setServoOff()


        
    def readStatus(self):
        pos = {}
        p = self.doCommand("RSTATS").strip().split(",")
        b1=int(p[0])
        b2=int(p[1])
        pos["step"] = b1>>0 &0x1
        pos["1cycle"] = b1>>1 &0x1
        pos["auto"] = b1>>2 &0x1
        pos["running"] = b1>>3 &0x1
        pos["safety_speed_operation"] = b1>>4 &0x1
        pos["teach"] = b1>>5 &0x1
        pos["play"] = b1>>6 &0x1
        pos["remote"] = b1>>7 &0x1
        pos["hold_pendant"] = b2>>1 &0x1
        pos["hold_external"] = b2>>2 &0x1
        pos["hold_command"] = b2>>3 &0x1
        pos["alarm"] = b2>>4 &0x1
        pos["error"] = b2>>5 &0x1
        pos["servo_on"] = b2>>6 &0x1
        return pos
    
    def setServoOn(self):
        stat=self.readStatus()
        if stat["alarm"]:
            raise Exception("Robot in alarm state before move")
        if not stat["servo_on"]:
            self.doCommand("SVON","1")

    def setServoOff(self):
        stat=self.readStatus()
        if stat["servo_on"]:
            self.doCommand("SVON","0")
            
    def doCommand(self, cmd, dat=""):
            try:
                    if self.single_cmd_mode:
                        self.reconnect()
                        self.sendStart()
                    self.checkConnected()
                    dataLen = len(dat)
                    if dataLen > 0:
                        dataLen += len('\r')
                    self.log( "dataLen = %d" % (dataLen))
                    message_to_send =  'HOSTCTRL_REQUEST %s %d\r\n' % (cmd, dataLen)
                    reply = self.sendAndReceive(message_to_send, '\r\n')
                    expected_reply = "OK: %s\r\n" %( cmd)
                    if reply != expected_reply:
                        raise Exception("Incorrect reply from command '%s'. Expected '%s' Actual '%s'" %( message_to_send, expected_reply, reply))
                    if dataLen != 0:
                        return self.sendAndReceive('%s\r\n' % dat, '\r')
                    return self.receive( '\r')
            finally:
                if self.single_cmd_mode:
                    self.disconnect()
          

    def gotoHome2(self):
        try:
            self.setServoOn()
            self.doCommand("PMOVJ","10,0,0,0,0,0,0,0,0,0,0,0,0,0")
            self.waitForEndOfMove()
        finally:
            self.setServoOff()
            
    def readPulses(self):
        """
        returns result of RPOSJ without terminator
        """
        return self.doCommand("RPOSJ").strip()

    def isAtHome2(self):
        return self.readPulses() == "0,0,0,0,0,0,0,0,0,0,0,0"


    
Detector_Robot_IP = "172.23.82.221"

class Robot():
    """
    class to manage movement of the motoman robot
    it holds position and pulses for that position
    requests to change position are only accepted if the pulses match those of the robot
    positions are changed in a particular order
    
    to use first home the robot and call resetPosition()
    if the robot is at expected home position the current robot positins are read and stored
    """
    def __init__(self, ip):
        self.__ctrl=Motoman(ip=ip)
        self.__pulses=""
        self.__position=Position()
        self.steps = Position()
        self.steps.X=self.steps.Y=self.steps.Z=10
        self.steps.RX=self.steps.RY=self.steps.RZ=5
        self.speed=10
        self.abort = True #must reset first
        self.usercoords=False
        
    def log(self,txt):
        handle_messages.log(None, txt)
    
    def resetPosition(self):
        if not self.__ctrl.isAtHome2():
            raise Exception("Error in resetPosition - robot not homed")
        self.__pulses = self.__ctrl.readPulses()
        self.__position = self.__ctrl.readRobotPositions()
        self.abort=False
        self.usercoords=False
        
    def __moveToStep(self, pos_delta, userCoordinates=0):
        if self.abort:
            raise Exception("Move aborted")
        
        if not pos_delta == Position():
            pos_end = self.__position+pos_delta
            self.__ctrl.moveUsingIncrements(self.__position, pos_end, steps=self.steps, speed=self.speed, userCoordinates=userCoordinates)
            pulses = self.__ctrl.readPulses()
            #read pulses before changing either member
            self.__position=pos_end
            self.__pulses = pulses

    
    def moveToDoNotSetUserCoords(self, pos):
        if self.abort:
            raise Exception("Move aborted. Call resetPosition to clear")
            
        actual=self.__ctrl.readPulses()
        if not self.__pulses==actual :
            raise Exception("Error in moveto. Robot not at expected position. Expected = %s Actual=%s" %(self.__pulses, actual))

        self.log("Moving to %s" % (pos))
        #move RZ=0
        self.__moveToStep(Position(RZ = -self.__position.RZ))
        #move RY=-45
        self.__moveToStep(Position(RY = -45 -self.__position.RY))
        self.__moveToStep(Position(Z= pos.Z-self.__position.Z, Y= pos.Y-self.__position.Y, X= pos.X-self.__position.X))
        self.__moveToStep(Position(RY= pos.RY-self.__position.RY))
        self.__moveToStep(Position(RZ= pos.RZ-self.__position.RZ))


    def moveTo(self, pos):
        if self.abort:
            raise Exception("Move aborted. Call resetPosition to clear")
            
        actual=self.__ctrl.readPulses()
        if not self.__pulses==actual :
            raise Exception("Error in moveto. Robot not at expected position. Expected = %s Actual=%s" %(self.__pulses, actual))

        if self.usercoords:
            pos2 = pos.getCopy()
            pos2.RY = self.__position.RY
            if pos2 != self.__position:
                raise Exception("Error in moveTo: In User Coord Mode. You can only change RY")
            self.__moveToStep(Position(RY= pos.RY-self.__position.RY), userCoordinates=2)
            
        else:
            self.log("Moving to %s" % (pos))
#            self.__moveToStep(Position(RY = -45 -self.__position.RY))
            self.__moveToStep(Position(Z= pos.Z-self.__position.Z, Y= pos.Y-self.__position.Y, X= pos.X-self.__position.X))
            orig=self.speed
            try:
#                self.speed=orig/2
#                self.__moveToStep(Position(RY = -80 -self.__position.RY))
#                self.speed=1
#                self.__moveToStep(Position(RY = -90 -self.__position.RY))
#                self.speed=orig/2
                self.__moveToStep(Position(RZ= pos.RZ-self.__position.RZ))
                self.setUserFrame()
                self.moveTo(self.__position + Position(RY= pos.RY-self.__position.RY))
            finally:
                self.speed=orig
        
        
    def abort(self):
        self.abort=True

    def gotoHome2(self):
        self.__ctrl.gotoHome2()

    def resetAlarm(self):
        self.__ctrl.resetAlarm()
        
    def getPosition(self):
        return self.__position.getCopy()

    def getPulses(self):
        return self.__pulses
    
    def setUserFrame(self):
        actual=self.__ctrl.readPulses()
        if not self.__pulses==actual :
            raise Exception("Error in moveto. Robot not at expected position. Expected = %s Actual=%s" %(self.__pulses, actual))

        org = self.__position
        xx = org.getCopy()
        xx.X += math.cos(org.RZ * math.pi/180.)
        xx.Y += math.sin(org.RZ * math.pi/180.)
        
        xy = org.getCopy()
        xy.X -= math.cos((90-org.RZ) * math.pi/180.)
        xy.Y += math.sin((90-org.RZ) * math.pi/180.)
        
        arg1 = "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0," %( org.X,org.Y,org.Z,org.RX,org.RY,org.RZ)
        arg2 = "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0," %( xx.X,xx.Y,xx.Z,xx.RX,xx.RY,xx.RZ)
        arg3 = "%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0," %( xy.X,xy.Y,xy.Z,xy.RX,xy.RY,xy.RZ)
        cmd= "2,"+arg1+arg2+arg3 +"0,"+"0,0,0,0,0,0"
        self.__ctrl.doCommand("WUFRAME",cmd)
        self.usercoords=True
        

"""
robot1 = motoman_controller.Motoman("172.23.82.221")
>>>xyz=robot1.readRobotPositions()
>>>xyz
1735.000,0.000,1400.000,180.000,-90.000,0.000,0,0,0.000,0.000,0.000,0.000,0.000,0.000
>>>xyz_final
1735.000,500.000,1400.000,180.000,-60.000,0.000,0,0,0.000,0.000,0.000,0.000,0.000,0.000
>>>robot1.moveToUsingIncremts(xyz, xyz_final, steps, speed=10)

>>>steps
5.000,5.000,5.000,1.000,1.000,1.000,0,0,0.000,0.000,0.000,0.000,0.000,0.000
>>>xyz_final
1735.000,500.000,1400.000,180.000,-60.000,0.000,0,0,0.000,0.000,0.000,0.000,0.000,0.000

>>>xyz_final
1735.000,500.000,1400.000,180.000,-60.000,0.000,0,0,0.000,0.000,0.000,0.000,0.000,0.000
>>>xyz_final2
1500.000,500.000,1400.000,180.000,-60.000,0.000,0,0,0.000,0.000,0.000,0.000,0.000,0.000
>>>robot1.moveToUsingIncremts(xyz_final, xyz_final2, steps, speed=10)
>>>xyz_final=xyz_final2
>>>xyz_final2 = copy.deepcopy(xyz_final)
>>>xyz_final2.Z=1200
>>>robot1.moveToUsingIncremts(xyz_final, xyz_final2, steps, speed=10)


obot1.gotoHome2()
>>>robotdelta=motoman_controller.Position(RY=45)
>>>robot1.moveByUsingIncremts(robotdelta,steps,speed=10)
>>>robotdelta=motoman_controller.Position(RZ=45)
>>>robot1.moveByUsingIncremts(robotdelta,steps,speed=10)
>>>robotdelta=motoman_controller.Position(RX=-45)
>>>robot1.moveByUsingIncremts(robotdelta,steps,speed=10)
>>>robot1.readRobotPositions()
1735.009,-0.072,1400.050,149.636,-8.421,59.640,1,0,0.020,0.000,0.000,0.000,0.000,0.000





"""

