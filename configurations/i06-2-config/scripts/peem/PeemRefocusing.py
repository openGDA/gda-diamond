from time import sleep
import cPickle as pickle;

from gda.jython.commands.GeneralCommands import alias
from gda.jython.commands import InputCommands

#the PEEM Refocusing Project

class PeemRefocusingClass():
    def __init__(self, name, cam1, cam1x, cam1y, cam1z, cam2, cam2x, cam2y, cam2z):

        self.name = name;
        
        self.cam1  = cam1;
        self.cam1x = cam1x;
        self.cam1y = cam1y;
        self.cam1z = cam1z
        self.cam2  = cam2;
        self.cam2x = cam2x;
        self.cam2y = cam2y;
        self.cam2z = cam2z
        if self.cam1x and self.cam1y:
            self.yag_motorised = True
        else:
            self.yag_motorised = False
        
        self.mx, self.my, self.x0, self.y0 = 0., 0., 0., 0.;
        
        self.pickle_file_name='/tmp/PeemRefocusingParameters.txt';

    def load_parameters(self):
        """Restore the pickled parameters from persistence"""
        try:
            in_stream = file(self.pickle_file_name, 'rb');
            [self.mx, self.my, self.x0, self.y0] = pickle.load(in_stream);
            in_stream.close();
        except IOError:
            print ("No previous pickled file numbers. Create new one");
            self.mx, self.my, self.x0, self.y0 = 0., 0., 0., 0.;
        
        return [self.mx, self.my, self.x0, self.y0];

    def save_parameters(self):
        """Save the parameters for persistence"""
        out_stream = file(self.pickle_file_name, 'wb');
        try:
            #Pickle the file number and dump to a file stream
            pickle.dump([self.mx, self.my, self.x0, self.y0], out_stream);
            out_stream.close();
        except IOError:
            print("Can not preserve the calibration parameters.");

    def calibration(self, d_yag=2):
        if self.yag_motorised :
            #pause to let user find beam spot on YAG screen
            InputCommands.requestInput("Use EPICS YAG motors to find the Beam spot, then press Enter...");
            xc1, yc1 = self.cam1x.getPosition(), self.cam1y.getPosition();
        else:
            xc1, yc1 = [float(x) for x in InputCommands.requestInput("Move YAG to find the Beam spot, input X and Y positions").split()]
            
        self.cam1.singleShot(1);
        [xz1, yz1, xsigma, ysigma, xysigma] = self.cam1.getCentroid();  # @UnusedVariable
        print("Point 1: (%f, %f) --> (%f, %f)" %(xz1, yz1, xc1, yc1));
        
        if self.yag_motorised:
            #Move to second point:
            self.cam1x.asynchronousMoveTo(xc1 + d_yag);
            self.cam1y.asynchronousMoveTo(yc1 + d_yag);
            while (self.cam1x.isBusy() or self.cam1y.isBusy()):
                sleep(1);
            sleep(5);
            xc2, yc2 = self.cam1x.getPosition(), self.cam1y.getPosition();
        else:
            xc2, yc2 = [float(x) for x in InputCommands.requestInput("Move YAG to 2nd position while still see the Beam spot, input X and Y positions").split()]
            
        self.cam1.singleShot(1);
        [xz2, yz2, xsigma, ysigma, xysigma] = self.cam1.getCentroid();  # @UnusedVariable
        print("Point 2: (%f, %f) --> (%f, %f)" %(xz2, yz2, xc2, yc2));
        
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
        [xz, yz, xzsigma, yzsigma, xyzsigma] = self.cam1.getCentroid();  # @UnusedVariable
        
        xc=self.mx*xz + self.x0;
        yc=self.my*yz + self.y0

        print("Point 1: (%f, %f) --> (%f, %f)" %(xz, yz, xc, yc));

        self.cam2x.asynchronousMoveTo(-xc);
        self.cam2y.asynchronousMoveTo(-yc);
        
        return [xc, yc]

    def center(self, camera, motor_x, motor_y, pixel_size):
        print("Adjusting camera position to centre the beam on the screen")
        camera.singleShot(1)
        [x0, y0, xzsigma, yzsigma, xyzsigma] = camera.getCentroid();  # @UnusedVariable

#        offsetPixelX=2452/2.0 -x0;
#        offsetPixelY=2056/2.0 - y0;
        offset_pixel_x=camera.getWidth()/2.0 - x0;
        offset_pixel_y=camera.getHeight()/2.0 - y0;
        
        offset_x=offset_pixel_x*pixel_size;
        offset_y =offset_pixel_y*pixel_size;

        motor_x.asynchronousMoveTo(motor_x.getPosition() - offset_x);
        motor_y.asynchronousMoveTo(motor_y.getPosition() + offset_y);
        
        return offset_x, offset_y;
        
    def centre_cam2(self, pixel_size=1.725e-4):
        return self.center(self.cam2, self.cam2x, self.cam2y, pixel_size)

from cameras.useCameras import camerac1, camerac2
prf=PeemRefocusingClass('PeemRefocusing', camerac1, None, None, u4m, camerac2, u1m, u2m, u3m);  # @UndefinedVariable - Spring beans

def calibration(d_yag=2):
    result = prf.calibration(d_yag);
    sleep(5)
    #centre()
    print("Type prf.save_parameters() to save the parameters.")
    print("Type prf.load_parameters() to load the parameters.")
    return result;

def findbeam():
    return prf.tracking();

def centre():
    return prf.centre_cam2();

alias("calibration")
alias("findbeam")
alias("centre")

print("-> Find peak calibration parameters loaded. ")
print("-> Activate camerac1 and type findbeam.")
prf.loadParameters()

