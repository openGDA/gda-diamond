from time import sleep
import math
import os;
import cPickle as pickle;


from gda.jython.commands.GeneralCommands import run, alias
from gda.jython.commands.Input import requestInput

import scisoftpy as dnp

#the PEEM Refocusing Project

class PeemRefocusingClass():
    def __init__(self, name, cam1, cam1x, cam1y, cam2, cam2x, cam2y):

        self.name = name;
        
        self.cam1  = cam1;
        self.cam1x = cam1x;
        self.cam1y = cam1y;
        self.cam2  = cam2;
        self.cam2x = cam2x;
        self.cam2y = cam2y;
        
        self.mx, self.my, self.x0, self.y0 = 0., 0., 0., 0.;
        
        self.pickleFileName='/tmp/PeemRefocusingParameters.txt';

    def loadParameters(self):
        """Restore the pickled parameters for persistence"""
        try:
            inStream = file(self.pickleFileName, 'rb');
            [self.mx, self.my, self.x0, self.y0] = pickle.load(inStream);
            inStream.close();
        except IOError:
            print "No previous pickled file numbers. Create new one";
            self.mx, self.my, self.x0, self.y0 = 0., 0., 0., 0.;
        
        return [self.mx, self.my, self.x0, self.y0];

    def saveParameters(self):
        """Save the parameters for persistence"""
        outStream = file(self.pickleFileName, 'wb');
        try:
            #Pickle the file number and dump to a file stream
            pickle.dump([self.mx, self.my, self.x0, self.y0], outStream);
            outStream.close();
        except IOError:
            print "Can not preserve the calibration parameters.";


    def calibrationOld(self, point1=[0, 0], point2=[2, 2]):
        xc1, yc1=point1;
        xc2, yc2=point2;

        #move to point 1
        self.cam1x.asynchronousMoveTo(xc1);
        self.cam1y.asynchronousMoveTo(yc1);
        while (self.cam1x.isBusy() or self.cam1y.isBusy()):
            sleep(1);
        self.cam1.singleShot(1);
        [xz1, yz1, xsigma, ysigma, xysigma] = self.cam1.getCentroid();
        print "Point 1: (%f, %f) --> (%f, %f)" %(xz1, yz1, xc1, yc1);
        

        #pause to let user find second point
        requestInput("Go back to EPICS YAG motors to move the Beam spot around, then press Enter...");
        #move to point 2
        self.cam1x.asynchronousMoveTo(xc2);
        self.cam1y.asynchronousMoveTo(yc2);
        while (self.cam1x.isBusy() or self.cam1y.isBusy()):
            sleep(1);
        self.cam1.singleShot(1);
        [xz2, yz2, xsigma, ysigma, xysigma] = self.cam1.getCentroid();
        print "Point 2: (%f, %f) --> (%f, %f)" %(xz2, yz2, xc2, yc2);
        
        #To calculate the mapping parameters
        self.x0=(xc1*xz2-xc2*xz1)/(xz2-xz1);
        self.mx=(xc2-xc1)/(xz2-xz1);
    
        self.y0=(yc1*yz2-yc2*yz1)/(yz2-yz1);
        self. my=(yc2-yc1)/(yz2-yz1);
        
        return [self.x0, self.y0, self.mx, self.my]

    def calibration(self, dYag=2):
        #pause to let user find second point
        requestInput("Use EPICS YAG motors to find the Beam spot, then press Enter...");
        xc1, yc1=self.cam1x.getPosition(), self.cam1y.getPosition();
        self.cam1.singleShot(1);
        [xz1, yz1, xsigma, ysigma, xysigma] = self.cam1.getCentroid();
        print "Point 1: (%f, %f) --> (%f, %f)" %(xz1, yz1, xc1, yc1);
        
        #Move to second point:
        self.cam1x.asynchronousMoveTo(xc1+dYag);
        self.cam1y.asynchronousMoveTo(yc1+dYag);
        while (self.cam1x.isBusy() or self.cam1y.isBusy()):
            sleep(1);

        sleep(5);
        xc2, yc2=self.cam1x.getPosition(), self.cam1y.getPosition();
        self.cam1.singleShot(1);
        [xz2, yz2, xsigma, ysigma, xysigma] = self.cam1.getCentroid();
        print "Point 2: (%f, %f) --> (%f, %f)" %(xz2, yz2, xc2, yc2);
        
        #To calculate the mapping parameters
        self.x0=(xc1*xz2-xc2*xz1)/(xz2-xz1);
        self.mx=(xc2-xc1)/(xz2-xz1);
    
        self.y0=(yc1*yz2-yc2*yz1)/(yz2-yz1);
        self. my=(yc2-yc1)/(yz2-yz1);

        #Restore to previous position:
        self.cam1x.asynchronousMoveTo(xc1);
        self.cam1y.asynchronousMoveTo(yc1);
        
        return [self.x0, self.y0, self.mx, self.my]
        
    def tracking(self):
        self.cam1.singleShot(1)
        [xz, yz, xzsigma, yzsigma, xyzsigma] = self.cam1.getCentroid();
        
        xc=self.mx*xz + self.x0;
        yc=self.my*yz + self.y0

        print "Point 1: (%f, %f) --> (%f, %f)" %(xz, yz, xc, yc);

        self.cam2x.asynchronousMoveTo(-xc);
        self.cam2y.asynchronousMoveTo(-yc);
        
        return [xc, yc]

    def center(self, camera, motorX, motorY, pixelSize):
        print "To adjust beam centre to the screen centre";
        camera.singleShot(1)
        [x0, y0, xzsigma, yzsigma, xyzsigma] = camera.getCentroid();

#        offsetPixelX=2452/2.0 -x0;
#        offsetPixelY=2056/2.0 - y0;
        offsetPixelX=camera.getWidth()/2.0 -x0;
        offsetPixelY=camera.getHeight()/2.0 - y0;
        
        offsetX=offsetPixelX*pixelSize;
        offsetY=offsetPixelY*pixelSize;

        motorX.asynchronousMoveTo(motorX.getPosition() - offsetX);
        motorY.asynchronousMoveTo(motorY.getPosition() + offsetY);
        
        return offsetX, offsetY;
        
    def centreCam2(self, pixelSize=1.725e-4):
        return self.center(self.cam2, self.cam2x, self.cam2y, pixelSize)

        
prf=PeemRefocusingClass('PeemRefocusing', campeem, yagx, yagy, camc2, c2x, c2y);

#prf.calibration();
#prf.saveParameters();
#prf.loadParameters();
#prf.tracking();

def cali(dYag):
    result = prf.calibration(dYag);
    sleep(5)
    #centre()
    print "Type prf.saveParameters() to save the parameters."
    print "Type prf.loadParameters() to load the parameters."
    return result;


def beam():
    return prf.tracking();

def centre():
    return prf.centreCam2();

alias("cali")
alias("beam")
alias("centre")


