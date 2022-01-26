

#####################################################################################
#
#The Class is for creating a device to control the Double Crystal Deflector  
#
#####################################################################################

#Planck's constant in joule X second (Js)
h=6.6260689633e-34

#velocity of light in vacuum in m/s
c=299792458 


#elementary charge in coulomb (C) or ampere X second (As)
e=1.60217648740e-19

#elementary charge in J
ev=1.60217648740e-19

#wavelength of 1eV photon in Angstrom (12398.4187573)
wperev=(h*c/ev)*1.0e10

from gda.device.scannable import ScannableBase;
from gda.device.scannable import ScannableMotionBase;
import math;

import __main__ as gdamain

class DoubleCrystalDeflectorClass(ScannableMotionBase):
    def __init__(self, name, wavelengthDevice, motorTheta, motorOmega, motorGamma, extraDevices=None, trackingDevices=[]):
        self.setName(name);
        self.setInputNames([name]);
        extraNames=["dcdomega", "dcdgamma"];
        outputFormat = ['%12.5f', '%12.5f', '%12.5f'];
        
        self.setExtraNames(extraNames);
        self.setOutputFormat(outputFormat);

        #Old crystal lattice plane spaces
#        self.d111=3.1355e-10;
#        self.d220=1.9201e-10;

		#New crystal lattice plane spaces
        self.d111=3.74065e-10;
        self.d220=2.29067e-10;

        self.motorTheta = motorTheta;#Incident beam angle
        self.motorGamma = motorGamma;#detector angle
        self.motorOmega = motorOmega;#rotating angle of the Eulerian cradle
        
        self.wavelengthDevice=wavelengthDevice;

        self.extraDevices=extraDevices;
        self.setExtraDevices(extraDevices);
        [self.theta0, self.omega0, self.gamma0]=self.getAngles();

        self.trackingDevices = [] if trackingDevices is None else trackingDevices
        trackingNames = [_x.name for _x in self.trackingDevices]
        self.extraNames = list(self.extraNames) + trackingNames
        trackingFormat = ["%12.5f"] * len(trackingNames)
        self.outputFormat = list(self.outputFormat) + trackingFormat


    def setExtraDevices(self, extraDevices):
        self.extraDevices=extraDevices;
        
        extraNames=["dcdomega", "dcdgamma"];
        outputFormat = ['%12.5f', '%12.5f', '%12.5f'];

        if self.extraDevices != None:
            for d in extraDevices:
                extraNames.extend(d.getInputNames()+d.getExtraNames())
                outputFormat.extend( d.getOutputFormat() );

        self.setExtraNames(extraNames);
        self.setOutputFormat(outputFormat);
        
        
    def setWavelengthDevice(self, wavelengthDevice):
        self.wavelengthDevice = wavelengthDevice;
        return self.wavelengthDevice.getPosition();
    
    #To get photon energy in keV based on wavelength in Angstrom
    def getEnergy(self, wavelength=None):
        if wavelength is None:
            wavelength = self.wavelengthDevice.getPosition();
        
        e=( (h*c/ev)*1.0e7 )/wavelength;
        return e;
    

    #To get wavelength in Angstrom based on photon energy in keV
    def getWavelength(self, energy=None):
        if energy is None:
            w=self.wavelengthDevice.getPosition();
        else:
            w=( (h*c/ev)*1.0e7 )/energy;
            
        if w < 0.01 or w > 100.0:
            print "Extreme Energy Range Warning: the energy for should be in the range of (100eV to 1000 KeV) ";
            raise ValueError("Energy Out Of Range Error");
        return w;
        
    def setThetaDevice(self, motorTheta):
        self.motorTheta = motorTheta;
        return self.motorTheta.getPosition();
        
    def setOmegaDevice(self, motorOmega):
        self.motorOmega = motorOmega;
        return self.motorOmega.getPosition();
    
    def setGammaDevice(self, motorGamma):
        self.motorGamma = motorGamma;
        return self.motorGamma.getPosition();
    
    def setLatticePlaneSpaces(self, d111, d220):
    	self.d111, self.d220 = d111, d220;
    	
    def getLatticePlaneSpaces(self):
    	print "Crystal Lattice Plane Spaces: d111=%e, d220=%e" %(self.d111, self.d220);
        return self.d111, self.d220;
    
    def getDelta2Theta(self):
#        d111=3.1355e-10;
#        d220=1.9201e-10;
        w=self.getWavelength()*1.0e-10;
        
        theta220=math.asin( w/(2.0*self.d220) );
        theta111=math.asin( w/(2.0*self.d111) );
        delta2theta=2.0*(theta220-theta111);
        
        return delta2theta;
        
    def getAngles(self):
#        th = self.motorTheta.getPosition();
#        ga = self.motorGamma.getPosition();
        omega = self.motorOmega.getPosition();
        om = math.radians( omega );

        delta2theta = self.getDelta2Theta();

        th = math.asin( math.sin(om) * math.sin(delta2theta) );
        ga = -1.0*math.asin( math.sin(math.pi/2.0 - om) * math.sin(delta2theta)  )
        
        return [math.degrees(th), omega, math.degrees(ga)];

    def calculateAngles(self, newTheta):
        #return new angles based on theta
        delta2theta = self.getDelta2Theta();
#        th=math.radians( self.motorTheta.getPositin() );
        th=math.radians( newTheta );
        om = math.asin( math.sin(th) / math.sin(delta2theta) );
        ga = -1.0*math.asin( math.sin(math.pi/2.0 - om) * math.sin(delta2theta)  );

        return [math.degrees(th), math.degrees(om), math.degrees(ga)];
        
    def getPosition(self):
        angles=self.getAngles();
        
        if self.extraDevices is not None:
            for d in self.extraDevices:
                extraPos=d.getPosition();
                if hasattr(extraPos, '__iter__'):
                    angles.extend(extraPos);
                else:
                    angles.append(extraPos);
            
        for device in self.trackingDevices:
            angles.append(device.getPosition())
        return angles;
    

    def asynchronousMoveTo(self, new_theta):
        [newTheta, newOmega, newGamma]=self.calculateAngles(new_theta);
        
        self.motorTheta.asynchronousMoveTo(newTheta);
        self.motorOmega.asynchronousMoveTo(newOmega)
        self.motorGamma.asynchronousMoveTo(newGamma)

        for device in self.trackingDevices:
            device.asynchronousMoveTo(newOmega)

        #To remember the angle positions
        [self.theta0, self.omega0, self.gamma0]=[newTheta, newOmega, newGamma];
        
    def getOmega0(self):
        return self.omega0;
	
    def getGamma0(self):
        return self.gamma0;

    def isBusy(self):
        return (self.motorTheta.isBusy() | self.motorOmega.isBusy() | self.motorGamma.isBusy());

    def toString(self):
        return self.getName() + ', '.join(out%posn for out, posn in zip(self.getOutputFormat(), self.getPosition()))

class DoubleCrystalDeflectorMonitorClass(ScannableMotionBase):
    def __init__(self, name, dcdDevice):
        self.setName(name);
        self.setInputNames(['dcdomega_requested']);
        self.setExtraNames(['dcdgamma_requested']);
        self.setOutputFormat(['%12.5f', '%12.5f'])

        self.dcdDevice = dcdDevice;#The DCD device to get the theoretical theta and omega and gamma
		
#        self.theta0 = None;
        self.omega0 = None;
        self.gamma0 = None;
        
    def asynchronousMoveTo(self, thetaX):
        return;

    def getPosition(self):
        self.omega0 = self.dcdDevice.getOmega0()
        self.gamma0 = self.dcdDevice.getGamma0();
        
        return self.omega0, self.gamma0;

    def isBusy(self):
        return False;


class ThetaXClass(ScannableMotionBase):
    def __init__(self, name, motorDCD, motorGamma, extraDevices=None):
        self.setName(name);
        self.setInputNames([name]);
        self.setExtraNames(["gamma_requested"]);
        self.setOutputFormat(['%12.5f', '%12.5f'])

        self.motorDcd = motorDCD;#The DCD to get the gamma0
        self.motorGamma = motorGamma;#detector angle

        self.extraDevices=extraDevices;
        self.setExtraDevices(extraDevices);
        
        self.gamma0 = self.getGamma0();

    def setExtraDevices(self, extraDevices):
        self.extraDevices=extraDevices;
        
        extraNames=["gamma_requested"];
        outputFormat = ['%12.5f', '%12.5f'];

        if self.extraDevices != None:
            for d in extraDevices:
                extraNames.extend(d.getInputNames()+d.getExtraNames())
                outputFormat.extend( d.getOutputFormat() );


        self.setExtraNames(extraNames);
        self.setOutputFormat(outputFormat);
        
    def getGamma0(self):
        self.gamma0=self.motorDcd.getGamma0();
        return self.gamma0;

    def asynchronousMoveTo(self, thetaX):
        self.getGamma0();
        newGamma=2.0*thetaX + self.gamma0;
        
#        print newGamma;
        self.motorGamma.asynchronousMoveTo(newGamma)

    def getPosition(self):
        self.getGamma0();
        ga = self.motorGamma.getPosition();
        if type(ga).__name__ == 'list' or type(ga).__name__ == 'tuple':
            ga=ga[0];
            
        tha = (ga - self.gamma0)/2.0;            
        angles=[tha, self.gamma0];
        if self.extraDevices is not None:
            for d in self.extraDevices:
                extraPos=d.getPosition();
                if hasattr(extraPos, '__iter__'):
                    angles.extend(extraPos);
                else:
                    angles.append(extraPos);
            
        return angles;

    def isBusy(self):
        return self.motorGamma.isBusy();


    def toString(self):
        return self.getName() + ', '.join(out%posn for out, posn in zip(self.getOutputFormat(), self.getPosition()))
    

class MomentumTransferDeviceClass(ScannableMotionBase):
    def __init__(self, name, wavelengthDevice, motorTheta, motor2Theta=None, extraDevices=None):
        self.setName(name);
        self.setInputNames([name]);
        self.thetaName=motorTheta.getName();
        self.setExtraNames([self.thetaName]);
        self.setOutputFormat(['%.5f', '%.5f'])


        self.wavelengthDevice=wavelengthDevice;
        self.motorTheta = motorTheta;#Incident beam angle
        self.motor2Theta = motor2Theta;#detector angle

        self.extraDevices=extraDevices;
        self.setExtraDevices(extraDevices);

    def setExtraDevices(self, extraDevices):
        self.extraDevices=extraDevices;
        
        extraNames=[self.thetaName];
        outputFormat = ['%.5f', '%.5f'];

        if self.extraDevices != None:
            for d in extraDevices:
                extraNames.extend(d.getInputNames()+d.getExtraNames())
                outputFormat.extend( d.getOutputFormat() );


        self.setExtraNames(extraNames);
        self.setOutputFormat(outputFormat);


    def setWavelengthDevice(self, wavelengthDevice):
        self.wavelengthDevice = wavelengthDevice;
        return self.wavelengthDevice.getPosition();
    
    #To get photon energy in keV based on wavelength in Angstrom
    def getEnergy(self, wavelength=None):
        if wavelength is None:
            wavelength = self.wavelengthDevice.getPosition();
        
        e=( (h*c/ev)*1.0e7 )/wavelength;
        return e;
    
    #To get wavelength in Angstrom based on photon energy in keV
    def getWavelength(self, energy=None):
        if energy is None:
            w=self.wavelengthDevice.getPosition();
        else:
            w=( (h*c/ev)*1.0e7 )/energy;
        return w;

    

    def setThetaDevice(self, motorTheta):
        self.motorTheta = motorTheta;
        return self.motorTheta.getPosition();
    
    def setTwoThetaDevice(self, motor2Theta):
        self.motor2Theta = motor2Theta;
        if self.motor2Theta is None:
            print "No detector angle 2theta to move"
            return;
        else:
            return self.motor2Theta.getPosition();

    def getQ(self, newTheta=None, wavelength=None):
        if newTheta is None: #use the current angles
            th = self.motorTheta.getPosition();
            if type(th).__name__ == 'list' or type(th).__name__ == 'tuple':
                th=th[0];
        else:#use a new angle
            th = newTheta;
        
        if wavelength is None: #use the current wavelength
            w=self.getWavelength();
        else:#use a new wavelength
            w=wavelength;
            
        rth=math.radians( th );
        q=4.0*math.pi*math.sin(rth)/w;

        return q;
        
    def getTheta(self, newQ, wavelength=None):
        if wavelength is None: #use the current wavelength
            w=self.getWavelength();
        else:#use a new wavelength
            w=wavelength;
            
        th= math.asin( (newQ*w)/(4.0*math.pi) );
        return math.degrees(th);

    def getPosition(self):
        th = self.motorTheta.getPosition();
        if type(th).__name__ == 'list' or type(th).__name__ == 'tuple':
            th=th[0];
            
        q=self.getQ( th );



        angles=[q, th];
        if self.extraDevices is not None:
            for d in self.extraDevices:
                extraPos=d.getPosition();
                if hasattr(extraPos, '__iter__'):
                    angles.extend(extraPos);
                else:
                    angles.append(extraPos);
            
        return angles;
    

    def asynchronousMoveTo(self, newQ):
        newTheta=self.getTheta(newQ);
        
        self.motorTheta.asynchronousMoveTo(newTheta);
        
        if self.motor2Theta is not None:
            self.motor2Theta.asynchronousMoveTo(2.0*newTheta);

    def isBusy(self):
        if self.motor2Theta is not None:
            return (self.motorTheta.isBusy() | self.motor2Theta.isBusy());
        else:
            return self.motorTheta.isBusy();
            

    def toString(self):
        return self.getName() + ', '.join(out%posn for out, posn in zip(self.getOutputFormat(), self.getPosition()))


#Example:

#motorWavelength, motorTheta, motorOmega, motorGamma = testMotor1, testMotor4, testMotor5, testMotor6;

#dcdtheta=DoubleCrystalDeflectorClass("dcdtheta", motorWavelength, motorTheta, motorOmega, motorGamma, [diff1vomega, diff1vdelta]);
#dcdtheta.setLatticePlaneSpaces(3.1355e-10, 1.9201e-10);
#dcdtheta.setLatticePlaneSpaces(3.74065e-10, 2.29067e-10);

#motor2Theta = testMotor6;
#q1=MomentumTransferDeviceClass("q1", motorWavelength, motorTheta, motor2Theta, [diff1vomega, diff1vdelta]);
#qdcd=MomentumTransferDeviceClass("q2", motorWavelength, dcdtheta, None, None);
