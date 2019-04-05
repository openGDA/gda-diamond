'''
Created on 25 Nov 2011

@author: tjs15132

Implementation of conversion from robot space to lab space and vice versa


m_DL - distance from detector surface to end of robot arm( this is a particular position in the robot software)
~250mm

m_R - sample to detector ~2000mm
m_SBX - distance between detector robot base and sample in robot X ( Diamond -Z). on a rail ~ 2500
need to add number of counts * slope from home position
m_SBY - distance between detector robot base and sample in robot Y ( Diamond -X). Fixed 1370mm
m_SBZ - distance between detector robot base and sample in robot Z ( Diamond Y). Fixed 226mm

m_theta - angle between line from sample to detector and Diamond Z in ZY plane
m_phi - angle between line from sample to detector and Diamond z in ZX plane

m_PHL - offset of center of pipe to end of pipe robot arm ~ 200mm
m_PHD - distance between sample and pipe robot ~ 2000mm
m_SB50_X - distance between pipe robot base and sample in robot X ( Diamond -Z). Fixed 1308mm
m_SB50_Y - distance between pipe robot base and sample in robot Y ( Diamond -X). Fixed 1707mm
m_SB50_Z - distance between pipe robot base and sample in robot Z ( Diamond Y). Fixed 80mm



The lab space is converted to robot space by the algorithm:

DLX=m_DL*cos(m_theta*PI/180)*cos(m_Phi*PI/180);// added due to the tool length
DLY=m_DL*cos(m_theta*PI/180)*sin(m_Phi*PI/180); // theta is Azim angle
DLZ=m_DL*sin(m_theta*PI/180);

DSX=m_R*cos(m_theta*PI/180)*cos(m_Phi*PI/180); // sample to end effector
DSY=m_R*cos(m_theta*PI/180)*sin(m_Phi*PI/180);
DSZ=m_R*sin(m_theta*PI/180);

m_RX=m_SBX-DLX-DSX; // coordinates in robot frame
m_RY=m_SBY-DLY-DSY;
m_RZ=m_SBZ+DLZ+DSZ;

m_RotY_azim=-90+m_theta;
m_RotZ_pol=m_Phi;

// small robot

//float Phi=90-m_Phi; // Not for NOW - only of rotated 90 deg
float Phi=m_Phi;

DPHX=m_PHL*cos(m_theta*PI/180)*cos(Phi*PI/180);
DPHY=m_PHL*cos(m_theta*PI/180)*sin(Phi*PI/180);
DPHZ=m_PHL*sin(m_theta*PI/180);

DS50X=m_PHD*cos(m_theta*PI/180)*cos(Phi*PI/180);
DS50Y=m_PHD*cos(m_theta*PI/180)*sin(Phi*PI/180);
DS50Z=m_PHD*sin(m_theta*PI/180);

m_R50_X=m_SB50_X-DPHX-DS50X;
m_R50_Y=m_SB50_Y-DPHY-DS50Y;
m_R50_Z=m_SB50_Z+DPHZ+DS50Z;

m_Rot50_Y=-90+m_theta; //azim
m_Rot50_Z=m_Phi; //pol


'''
import scisoftpy as np
import math


class Position():
    def __init__(self, X=0., Y=0.,Z=0.,RX=0.,RY=0.,RZ=0., ext1=0.):
        self.X=X
        self.Y=Y
        self.Z=Z
        self.RX=RX
        self.RY=RY
        self.RZ=RZ
        self.type="0"
        self.tool = "0"
        self.ext1=ext1
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
        res.ext1 -= other.ext1
        return res

    def __add__(self,other):
        res=self.getCopy()
        res.X += other.X
        res.Y += other.Y
        res.Z  += other.Z
        res.RX += other.RX
        res.RY += other.RY
        res.RZ += other.RZ
        res.ext1 += other.ext1
        return res
    
    def getCopy(self):
        return copy.deepcopy(self)
    
    def __eq__(self,other):
        return isinstance(other, Position) and self.withinResolution(other, res=0.)

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
        result.ext1 = self.__getValueForMoveTowards(result.ext1, final.ext1, steps.ext1, res)
        return result
    
    def withinResolution(self,other,res=.001):
        return (math.fabs(self.X - other.X) <= res) and \
            (math.fabs(self.Y - other.Y) <= res) and \
            (math.fabs(self.Z - other.Z) <= res) and \
            (math.fabs(self.RX - other.RX) <= res) and \
            (math.fabs(self.RY - other.RY) <= res) and \
            (math.fabs(self.RZ - other.RZ) <= res) and \
            (math.fabs(self.ext1 - other.ext1) <= res) 
    



def calcRobotMotorsBasic(DL=250, DD=2000, SBX=2500, SBY=1370, SBZ=226, theta=60.,phi=60, PHL=200, PHD=2000, SB50X=1308, SB50Y=1707, SB50Z=80):
    theta_rad = theta * 180./np.pi
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    phi_rad = phi * 180./np.pi
    cos_phi = math.cos(phi_rad)
    sin_phi = math.sin(phi_rad)

    DLX = DL * cos_theta * cos_phi
    DLY = DL * cos_theta * sin_phi
    DLZ = DL * sin_theta

    DDX = DD * cos_theta * cos_phi
    DDY = DD * cos_theta * sin_phi
    DDZ = DD * sin_theta

    RX = SBX -DLX-DDX
    RY = SBY -DLY-DDY
    RZ = SBZ +DLZ+DDZ

    RotY = -90 + theta;
    RotZ = phi;
    
    
    DL50X = PHL * cos_theta * cos_phi
    DL50Y = PHL * cos_theta * sin_phi
    DL50Z = PHL * sin_theta

    DR50X = PHD * cos_theta * cos_phi
    DR50Y = PHD * cos_theta * sin_phi
    DR50Z = PHD * sin_theta

    R50X = SB50X -DLX-DDX
    R50Y = SB50Y -DLY-DDY
    R50Z = SB50Z +DLZ+DDZ
    
    Rot50Y= -90 + theta 
    Rot50Z = phi

    return (RX,RY,RZ,RotY,RotZ,R50X,R50Y,R50Z,Rot50Y,Rot50Z )

from Jama import Matrix
def calcRobotMotors(theta=60.,phi=60, DL=250, DD=2000, 
                    SBX=2500, SBY=1370, SBZ=226,  PHL=200, robotPointsAtSample=True):
    return calcSingleRobotMotors(
                                angleSampleToDetectorAboutDiamondX=-theta,
                                angleSampleToDetectorAboutDiamondY=phi,
                                distFromSampleToActivePoint=DL+DD,
                                distFromSampleToActivePointx=PHL,
                                robotPointsAtSample=robotPointsAtSample,
                                offsetInRobotXFromControlPointToDiffractometerCentre=SBX,
                                offsetInRobotYFromControlPointToDiffractometerCentre=SBY,
                                offsetInRobotZFromControlPointToDiffractometerCentre=SBZ )
def calcRobotMotorsInverse(position, SBX=2500, SBY=1370, SBZ=226, robotPointsAtSample=True, PHL=200):
#, SB50X=1308, SB50Y=1707, SB50Z=80):
    
    inverse = calcSingleRobotMotorsInverse(position=position,
                                robotPointsAtSample=robotPointsAtSample,
                                distFromSampleToActivePointx=PHL, 
                                offsetInRobotXFromControlPointToDiffractometerCentre=SBX,
                                offsetInRobotYFromControlPointToDiffractometerCentre=SBY,
                                offsetInRobotZFromControlPointToDiffractometerCentre=SBZ )
    
    #reverse theta
    inverse = list(inverse)
    inverse[0]= -1*inverse[0]

    return inverse

def getDetectorRobotPositionFromThetaPhi(theta=60.,phi=60, DL=250, DD=2000, 
                    SBX=2500, SBY=1370, SBZ=226):
    """
    Returns the position of the robot motors required for a certain theta and phi where:
    
    theta - angle between line from sample to detector and Diamond Z in ZY plane
    phi - angle between line from sample to detector and Diamond z in ZX plane
    
    DL - distance from detector surface to end of robot arm( this is a particular position in the robot software)~250mm
    DD - sample to detector ~2000mm    
    SBX - distance between detector robot base and sample in robot X ( Diamond -Z). on a rail ~ 2500
            need to add number of counts * slope from home position
    SBY - distance between detector robot base and sample in robot Y ( Diamond -X). Fixed 1370mm
    SBZ - distance between detector robot base and sample in robot Z ( Diamond Y). Fixed 226mm

    """
    
    return calcSingleRobotMotors(
                                angleSampleToDetectorAboutDiamondX=-theta,
                                angleSampleToDetectorAboutDiamondY=phi,
                                distFromSampleToActivePoint=DL+DD,
                                distFromSampleToActivePointx=0,
                                robotPointsAtSample=True,
                                offsetInRobotXFromControlPointToDiffractometerCentre=SBX,
                                offsetInRobotYFromControlPointToDiffractometerCentre=SBY,
                                offsetInRobotZFromControlPointToDiffractometerCentre=SBZ )


def calcSingleRobotMotors(angleSampleToDetectorAboutDiamondX=45,
                          angleSampleToDetectorAboutDiamondY=45,
                          samplePositionOnDiamondXY_X=0,
                          samplePositionOnDiamondXY_Y=0,
                          distFromSampleToActivePoint=1000, 
                          distFromSampleToActivePointx=0, 
                          robotPointsAtSample=True,
                          offsetInRobotXFromControlPointToDiffractometerCentre=1000, 
                          offsetInRobotYFromControlPointToDiffractometerCentre=1000,
                          offsetInRobotZFromControlPointToDiffractometerCentre=1000 ):

    if robotPointsAtSample:
        distFromSampleToActivePointx = 0

#    print "angleSampleToDetectorAboutDiamondX=%s" %(angleSampleToDetectorAboutDiamondX)
#    print "angleSampleToDetectorAboutDiamondY=%s" %(angleSampleToDetectorAboutDiamondY)
#    print "samplePositionOnDiamondXY_X=%s" %(samplePositionOnDiamondXY_X)
#    print "samplePositionOnDiamondXY_Y=%s" %(samplePositionOnDiamondXY_Y)
#    print "distFromSampleToActivePoint=%s" %(distFromSampleToActivePoint)
#    print "distFromSampleToActivePointx=%s" %(distFromSampleToActivePointx)
#    print "robotPointsAtSample=%s" %(robotPointsAtSample)
#    print "offsetInRobotXFromControlPointToDiffractometerCentre=%s" %(offsetInRobotXFromControlPointToDiffractometerCentre)
#    print "offsetInRobotYFromControlPointToDiffractometerCentre=%s" %(offsetInRobotYFromControlPointToDiffractometerCentre)
#    print "offsetInRobotZFromControlPointToDiffractometerCentre=%s" %(offsetInRobotZFromControlPointToDiffractometerCentre)
    """
    consider the vector from sample to robot of length DL + DR . In cartesian space of robot :
    rotation of Diamond coordinates by rotation theta about X and phi about Y
    labXYZ =  MRotY * MRotX * robotXYZ
    """
    #asumme distFromSampleToActivePointx points along x direction in frame rotated by angleSampleToDetectorAboutDiamondX & angleSampleToDetectorAboutDiamondY
    robotEndFromSampleInDetectorAtSampleXYZ = getVectorFromComponents(distFromSampleToActivePointx,0,distFromSampleToActivePoint)
        
    
    #Matrix to rotate from XYZ at sample with z along line to detector to Diamond
    M1 = getMRot(angleSampleToDetectorAboutDiamondX,angleSampleToDetectorAboutDiamondY,0.)

    #translationFromSampleto centre of diffractometer
    T1 = getVectorFromComponents(
                samplePositionOnDiamondXY_X,
                samplePositionOnDiamondXY_Y,
                0.)

    robotEndInDiamondXYZ=M1.times(robotEndFromSampleInDetectorAtSampleXYZ).plus(T1)
    
    T2 = getTranslationfromDiffractometerCentreToRobot(offsetInRobotXFromControlPointToDiffractometerCentre,
                                         offsetInRobotYFromControlPointToDiffractometerCentre,
                                         offsetInRobotZFromControlPointToDiffractometerCentre)

    M2 = getTransformFromDiamondXYZToRobotXYZ()

    robotEndFromRobotInRobotXYZ = M2.times(robotEndInDiamondXYZ.minus(T2))


    X = robotEndFromRobotInRobotXYZ.get(0,0)
    Y = robotEndFromRobotInRobotXYZ.get(1,0)
    Z = robotEndFromRobotInRobotXYZ.get(2,0)

    """
    Unit vector along line from sample to detector in DiamondXYZ
    """
    #transform into robot XYZ
        
    #is this about Y or from Y?
    if robotPointsAtSample :
        RY = -angleSampleToDetectorAboutDiamondX -90;
        RZ = angleSampleToDetectorAboutDiamondY;
    else :
        U = getVectorFromComponents(-1,0,0)
        unityInDiamondZ= M1.times(U)
        RY = -angleSampleToDetectorAboutDiamondX;
        RZ=math.atan2(unityInDiamondZ.get(0,0),unityInDiamondZ.get(2,0)) *180/math.pi
        RZ=angleSampleToDetectorAboutDiamondY

    return Position(X=X,Y=Y,Z=Z,RY=RY,RZ=RZ )

def calcSingleRobotMotorsInverse(position= Position(),
                          distFromSampleToActivePointx=0, 
                          robotPointsAtSample=True,
                          offsetInRobotXFromControlPointToDiffractometerCentre=1000, 
                          offsetInRobotYFromControlPointToDiffractometerCentre=1000,
                          offsetInRobotZFromControlPointToDiffractometerCentre=1000 ):

    """
    consider the vector from sample to robot of length DL + DR . In cartesian space of robot :
    rotation of Diamond coordinates by rotation theta about X and phi about Y
    labXYZ =  MRotY * MRotX * robotXYZ
    """
    #position of robot end in frame of reference centred at sample rotated so that z axis
    #points towards the detector
    
    RX=position.X
    RY=position.Y
    RZ=position.Z
    RotY=position.RY
    RotZ=position.RZ
    robotEndFromRobotInRobotXYZ=getVectorFromComponents(RX,RY,RZ)

    M2 = getTransformFromRobotXYZToDiamondXYZ()

    T2 = getTranslationfromDiffractometerCentreToRobot(offsetInRobotXFromControlPointToDiffractometerCentre,
                                         offsetInRobotYFromControlPointToDiffractometerCentre,
                                         offsetInRobotZFromControlPointToDiffractometerCentre)

    robotEndInDiamondXYZ = M2.times(robotEndFromRobotInRobotXYZ).plus(T2)


    if robotPointsAtSample:
        angleSampleToDetectorAboutDiamondX = -RotY-90
        angleSampleToDetectorAboutDiamondY = RotZ;
    else:
        angleSampleToDetectorAboutDiamondX = -RotY
        angleSampleToDetectorAboutDiamondY = RotZ;
        
        
    M1=getMRot(angleSampleToDetectorAboutDiamondX,angleSampleToDetectorAboutDiamondY,0.)    
    if not robotPointsAtSample:
        """
        offset of robotEnd is due to distFromSampleToActivePointx
            assume distFromSampleToActivePointx points along x direction in frame rotated by angleSampleToDetectorAboutDiamondX & angleSampleToDetectorAboutDiamondY
        """
        U = getMRotY(90).times(getVectorFromComponents(0,0,distFromSampleToActivePointx))
        offsetInDiamondXY= M1.times(U)
        robotEndInDiamondXYZ = robotEndInDiamondXYZ.minus(offsetInDiamondXY)
    
    """
    U = unit vector in labXYZ along direciton given by angleSampleToDetectorAboutDiamondX and angleSampleToDetectorAboutDiamondY
    L is a scalar
    P is vector in labXYZ to point where L * U meets z=0 plane.

    L*U + P = robotEndInDiamondXYZ
    
    P(z) =0
    so L = robotEndInDiamondXYZ.z / U.z
    
    P.x =  robotEndInDiamondXYZ.x   -L*U.x
    P.y =  robotEndInDiamondXYZ.y   -L*U.y
    
    Distance from P to detector = L 
    """
    U = M1.times(getVectorFromComponents(0,0,1))

    distFromSampleToActivePoint = robotEndInDiamondXYZ.get(2,0)/U.get(2,0)
    samplePositionOnDiamondXY_X = robotEndInDiamondXYZ.get(0,0) - U.get(0,0)*distFromSampleToActivePoint
    samplePositionOnDiamondXY_Y = robotEndInDiamondXYZ.get(1,0) - U.get(1,0)*distFromSampleToActivePoint
    
    
    return (angleSampleToDetectorAboutDiamondX,angleSampleToDetectorAboutDiamondY, 
            samplePositionOnDiamondXY_X, samplePositionOnDiamondXY_Y, distFromSampleToActivePoint,)


def getTranslationfromDiffractometerCentreToRobot(
                                                  offsetInRobotXFromControlPointToDiffractometerCentre, 
                                                  offsetInRobotYFromControlPointToDiffractometerCentre,
                                                  offsetInRobotZFromControlPointToDiffractometerCentre):
    return getVectorFromComponents(
                offsetInRobotYFromControlPointToDiffractometerCentre,
                offsetInRobotZFromControlPointToDiffractometerCentre,
                offsetInRobotXFromControlPointToDiffractometerCentre)
    
def getTransformFromDiamondXYZToRobotXYZ():
    return Matrix ( [ [0,0,-1], [-1, 0, 0], [0, 1, 0] ])

def getTransformFromRobotXYZToDiamondXYZ():
    return getTransformFromDiamondXYZToRobotXYZ().inverse()
    

def getVectorFromRotations(position):
   return getMRotZ(position.RZ).times(getMRotY(position.RY).times(getMRotX(position.RX).times(getVectorFromComponents(1,0,0))))  

def getThetaPhiOfRobotVectorFromRotations(position):
    """
    prints out the angle made to Z axis in RX plane (theta) and andle made to Y axis in XY plane(phi)
    of reference vector of robot ( when homed is straight up theta=0 and phi = 0)
    """
    res = getMRotZ(position.RZ).times(getMRotY(position.RY).times(getMRotX(position.RX).times(getVectorFromComponents(1,0,0))))
    X = res.get(0,0)
    Y = res.get(1,0)
    Z = res.get(2,0)
    theta = math.atan2(X,Z)*180/math.pi
    theta1 = math.atan2(Y,Z)*180/math.pi
    phi = math.atan2(Y,X)*180/math.pi
    print "theta = %f theta1 = %f phi =%f" %(theta, theta1, phi)  

def getVectorFromComponents(x, y, z):
    return Matrix ( [[x], [y], [z]] )
    
    
def getMRot( angleAboutX, angleAboutY, angleAboutZ):
    return getMRotZ(angleAboutZ).times(getMRotY(angleAboutY).times(getMRotX(angleAboutX)))

def getMRotX( angle):
    ( cos, sin) = getCosAndSin(angle)
    return Matrix ([ [1,0,0], [0, cos, -sin], [0, sin, cos] ])

def getMRotY( angle):
    ( cos, sin) = getCosAndSin(angle)
    return Matrix ([ [cos, 0, sin], [0,1,0], [-sin, 0, cos] ])

def getMRotZ( angle):
    ( cos, sin) = getCosAndSin(angle)
    return Matrix ( [[cos, -sin, 0], [ sin, cos, 0 ], [0,0,1]])
  

def getCosAndSin(angle):
    angle_rad = angle *np.pi /180.
    return ( math.cos(angle_rad), math.sin(angle_rad))
  
  
  
import unittest
class TestConversion(unittest.TestCase):
    def __init__(self, parameters):
        unittest.TestCase.__init__(self)
        self.parameters = parameters

    def runTest(self):
        if not (self.parameters is None):
#            res0 = calcRobotMotorsBasic( DL=self.parameters["DL"], DD=self.parameters["DD"], theta=self.parameters["theta"],phi=self.parameters["phi"], 
#                                        PHL=self.parameters["PHL"], PHD=self.parameters["PHD"], SBX=self.parameters["SBX"], SBY=self.parameters["SBY"],
#                                        SBZ=self.parameters["SBZ"])
            position= calcRobotMotors(theta=self.parameters["theta"], phi=self.parameters["phi"],
                                 DL=self.parameters["DL"], DD=self.parameters["DD"],
                                 PHL=self.parameters["PHL"], robotPointsAtSample=self.parameters["robotPointsAtSample"],
                                 SBX=self.parameters["SBX"], SBY=self.parameters["SBY"],
                                        SBZ=self.parameters["SBZ"]
                                 )
            if not self.parameters["expectedPosition"] == None:
                self.assertEqual(self.parameters["expectedPosition"], position)
            res2 = calcRobotMotorsInverse(position=position,
                                           robotPointsAtSample=self.parameters["robotPointsAtSample"],
                                          PHL=self.parameters["PHL"],  
                                          SBX=self.parameters["SBX"], SBY=self.parameters["SBY"],
                                        SBZ=self.parameters["SBZ"]) 
#            print "\nres0 = %s " % (`res0`)
#            print "res = %s " % (`res`)
#            print "res2 = %s " % (`res2`)
            self.assertEqual( self.parameters["theta"], round(res2[0],5))
            self.assertEqual(  self.parameters["phi"] , round(res2[1],5))
            self.assertEqual(  0. , round(res2[2],5)) #sample position X
            self.assertEqual(  0. , round(res2[3],5)) #sample position Y
            self.assertEqual(  self.parameters["DL"] + self.parameters["DD"] , round(res2[4],5))
#            self.assertEqual(  self.parameters["theta"] , round(res2[5],5))
#            self.assertEqual(  self.parameters["phi"] , round(res2[6],5))
#            self.assertEqual(  0. , round(res2[7],5))
#            self.assertEqual(  0. , round(res2[8],5))
#            self.assertEqual(  self.parameters["PHD"]  , round(res2[9],5))
import sys;
def makeTest( theta=0., phi=0., DL=250, DD=2000, PHL=200, PHD=2000, SBX=2500, SBY=1370, SBZ=226, robotPointsAtSample=True
              , expectedPosition=None):
    d = {}
    d["theta"]=theta
    d["phi"]=phi
    d["DL"]=DL
    d["DD"]=DD
    d["SBX"]=SBX
    d["SBY"]=SBY
    d["SBZ"]=SBZ
    d["robotPointsAtSample"]=robotPointsAtSample
    d["PHL"]=PHL
    d["expectedPosition"] = expectedPosition
    return TestConversion(d)

def suite():
    ts = unittest.TestSuite()
    ts.addTest(makeTest(theta=0,phi=0, DL=0, DD=1000, SBX=1000, SBY=1000, SBZ=1000,  robotPointsAtSample=True, expectedPosition=Position(X=0, Y=1000, Z=-1000, RX=0, RY=-90, RZ=0)))
    ts.addTest(makeTest(theta=60,phi=0, DL=0, DD=1000, SBX=1000, SBY=1000, SBZ=1000))
    ts.addTest(makeTest(theta=0,phi=60, DL=0, DD=1000, SBX=1000, SBY=1000, SBZ=1000))
    ts.addTest(makeTest(theta=60,phi=0))
    ts.addTest(makeTest(theta=0,phi=60))
    ts.addTest(makeTest(theta=30,phi=60))
    ts.addTest(makeTest(theta=60,phi=30))
    ts.addTest(makeTest(theta=60,phi=30, DL=20, DD=1000, PHL=50, PHD=500))

# pipe detector setup the following fail at the moment
#    ts.addTest(makeTest(theta=0,phi=0, DL=0, DD=1000, SBX=1000, SBY=1000, SBZ=1000, robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=60,phi=0, DL=0, DD=1000, SBX=1000, SBY=1000, SBZ=1000, robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=0,phi=60, DL=0, DD=1000, SBX=1000, SBY=1000, SBZ=1000, robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=60,phi=0,robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=0,phi=60, robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=30,phi=60,robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=60,phi=30,robotPointsAtSample=False))
#    ts.addTest(makeTest(theta=60,phi=30, DL=20, DD=1000, PHL=50, PHD=500,robotPointsAtSample=False))
    return ts

def run_tests():
    runner = unittest.TextTestRunner(stream=sys.stdout, descriptions=1, verbosity=1)
    runner.run(unittest.TestSuite(suite()))
    print "End of tests"
    
    

import os, sys, socket 
import time
from gdascripts.messages import handle_messages
import copy
import math

class Motoman(object):
    def __init__(self, ip, timeout=5, single_cmd_mode=True):
        self.ip = ip
        self.connected=False
        self.verbose=False
        self.timeout=timeout
        self.single_cmd_mode = single_cmd_mode

    def log(self,txt):
        if self.verbose:
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
                raise IOError("Reply timeout reply so far %s" %(reply))
        return reply

    def readCurrentPositionInJointSpace(self):
        return self.doCommand("RPOSJ").strip()

    def readCurrentPositionInBaseSpaceWithExternalAxis(self):
        return self.doCommand("RPOSC","0,1").strip()

    def readCurrentPositionInRobotSpaceWithExternalAxis(self):
        return self.doCommand("RPOSC","1,1").strip()

    def readCurrentPositionInUser1SpaceWithExternalAxis(self):
        return self.doCommand("RPOSC","2,1").strip()

    def getUserCoordinateData(self, userCoord=2):
        return self.doCommand("RUFRAME",`userCoord`).strip()
        
        
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
            if ctr > 1000:
                raise Exception("Move did not complete in time - 100s")
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
        
    def moveIncrementalInRobotSpace(self, xyz=Position(), speed=1, doIt=True, userCoordinates=0):
        self.log("moveIncrementalInRobotSpacem called for xys=%s" %(xyz))
        arg = ""
        arg += "0" +"," #speed selection `0- V 1- VR, VR may be better for angles only, 
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
        
    def moveUsingIncrements(self, xyz_start=None, xyz_final=None, steps=None, res=0.001, speed=1, doIt=True, userCoordinates=0):
        self.setServoOn()
        try:
            self.abort = False
            prev_pos = xyz_start
            start_time=time.clock()
            while not prev_pos.withinResolution(xyz_final,res):
                now=time.clock()
                if now-start_time > 1800:
                    raise Exception("Time to move > 1800s")
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
            #go to home at speed 1 
            self.doCommand("PMOVJ","1,0,0,0,0,0,0,0,0,0,0,0,0,0")
            self.waitForEndOfMove()
            if not self.isAtHome2():
                raise Exception("gotoHome2 error - trying resetting alarm ")
            return True
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
Detector_Robot_Pipe_IP="172.23.82.220"

class Robot():
    """
    class to manage movement of the motoman robot
    it holds position and pulses for that position
    requests to change position are only accepted if the pulses match those of the robot
    positions are changed in a particular order
    
    to use first home the robot and call resetPosition()
    if the robot is at expected home position the current robot positions are read and stored
    """
    def __init__(self, ip):
        self.__ctrl=Motoman(ip=ip)
        self.__pulses=""
        self.__position=Position()
        self.steps = Position()
        self.steps.X=self.steps.Y=self.steps.Z=1000
        self.steps.RX=self.steps.RY=self.steps.RZ=300
        self.steps.ext1 = 100
        self.speed=1
        self.abort = True #must reset first
        self.usercoords=False
        self.mustBeAtHomeForreset=True
        
    def getCtrl(self):
        """
        Not to be used by normal users.
        """
        return self.__ctrl
    
    def log(self,txt):
        handle_messages.log(None, txt)
    
    def resetPosition(self):
        if self.mustBeAtHomeForreset and (not self.__ctrl.isAtHome2()):
            raise Exception("Error in resetPosition - robot not homed")
        self.__pulses = self.__ctrl.readPulses()
        self.__position = self.__ctrl.readRobotPositions()
        self.abort=False
        self.usercoords=False
        return True
        
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
            self.__moveToStep(Position(ext1= pos.ext1-self.__position.ext1))
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
        return self.__ctrl.gotoHome2()

    def resetAlarm(self):
        self.__ctrl.resetAlarm()
        
    def getPosition(self):
        return self.__position.getCopy()
    
    def getControllerPositions(self):
        return self.__ctrl.readRobotPositions()

    def getControllerPulses(self):
        return self.__ctrl.readPulses()

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
        

    def calcDetectorPositions(self, theta=0.,phi=60, DL=250, DD=2000, SBX=2500, SBY=1370, SBZ=226):
        return calcSingleRobotMotors(
                                angleSampleToDetectorAboutDiamondX=-theta,
                                angleSampleToDetectorAboutDiamondY=phi,
                                distFromSampleToActivePoint=DL+DD,
                                distFromSampleToActivePointx=0,
                                robotPointsAtSample=True,
                                offsetInRobotXFromControlPointToDiffractometerCentre=SBX,
                                offsetInRobotYFromControlPointToDiffractometerCentre=SBY,
                                offsetInRobotZFromControlPointToDiffractometerCentre=SBZ )        

    def calcPipePositions(self, theta=0.,phi=60, DL=0, DD=2000, SBX=1308, SBY=1707, SBZ=80, distFromSampleToActivePointx=200):
        return calcSingleRobotMotors(
                                angleSampleToDetectorAboutDiamondX=-theta,
                                angleSampleToDetectorAboutDiamondY=phi,
                                distFromSampleToActivePoint=DL+DD,
                                distFromSampleToActivePointx=distFromSampleToActivePointx,
                                robotPointsAtSample=True,
                                offsetInRobotXFromControlPointToDiffractometerCentre=SBX,
                                offsetInRobotYFromControlPointToDiffractometerCentre=SBY,
                                offsetInRobotZFromControlPointToDiffractometerCentre=SBZ )      
        

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


    
