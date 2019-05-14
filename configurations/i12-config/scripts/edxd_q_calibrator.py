import math
from gda.analysis.io import NexusLoader

from uk.ac.diamond.scisoft.analysis.fitting.functions import Quadratic, Gaussian
from uk.ac.diamond.scisoft.analysis.optimize import GeneticAlg
from uk.ac.diamond.scisoft.analysis.fitting import Fitter 

from org.eclipse.january.dataset import DatasetFactory

from time import sleep
from gda.analysis import ScanFileHolder, RCPPlotter
from fittingtest import plotNPeaks
import string

run("fittingtest") #@UndefinedVariable

class q_refinement() :    
    
# for scans in EH2 with EH2 collimator, 4.5 degree take-off angle with Si 640d lattice parameter - 9/8/11 from Thomas updated on 10/08/2011 add 3 more
    calibrants = {50.3526:2.0036,
                  82.2254:3.2719,
                  96.4179:3.8366,
                  116.2843:4.6271,
                  126.7179:5.0423,
                  142.4186:5.6671,
                  151.0577:6.0108,
                  164.4508:6.5438,
                  171.9868:6.8436}
    
#    calibrants = {45.29:2.004,
#                  73.96:3.272,
#                  86.72:3.837,
#                  104.59:4.628,
#                  113.97:5.043,
#                  128.09:5.668,
#                  135.87:6.012,
#                  147.91:6.545,
#                  154.69:6.844}

    def read_calibrants_file(self, filename):
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        newlines=[]
        for line in lines:
            if '#' not in line:
                newlines+=line
            
        lines = map(string.split, map(string.strip, newlines))
        for x in lines:
            self.calibrants[float(x[0])]=float(x[1])
        print "set calibrants values:"
        for key in self.calibrants.iterkeys(): 
            print str(key), " : ", str(self.calibrants[key])
            
    def collectdata(self,time) :
        # collect the data
        self.ds = edxd.acquire(time) #@UndefinedVariable
        
    def loadOldData(self,filename):
        sfh = ScanFileHolder()
        sfh.load(NexusLoader(filename))
        self.ds = []
        self.ds += [sfh[0][0]]
        self.ds += [sfh[3][0]]
        self.ds += [sfh[6][0]]
        self.ds += [sfh[9][0]]
        self.ds += [sfh[12][0]]
        self.ds += [sfh[15][0]]
        self.ds += [sfh[18][0]]
        self.ds += [sfh[21][0]]
        self.ds += [sfh[24][0]]
        self.ds += [sfh[27][0]]
        self.ds += [sfh[30][0]]
        self.ds += [sfh[33][0]]
        self.ds += [sfh[36][0]]
        self.ds += [sfh[39][0]]
        self.ds += [sfh[42][0]]
        self.ds += [sfh[45][0]]
        self.ds += [sfh[48][0]]
        self.ds += [sfh[51][0]]
        self.ds += [sfh[54][0]]
        self.ds += [sfh[57][0]]
        self.ds += [sfh[60][0]]
        self.ds += [sfh[63][0]]
        self.ds += [sfh[66][0]]
        self.ds += [sfh[69][0]]
        

    def matchPeaks(self,peak_positions,calibration_peak_energy):
        diff = []
        for i in range(len(peak_positions)):
            diff += [(math.fabs(peak_positions[i]-calibration_peak_energy),i, peak_positions[i])]
        diff.sort()
        return diff[0]
    

    def fitPeaks(self, number_of_peaks_to_fit, smoothing,  channel):

        # get the energy scale
        energys = DataSet(edxd.getSubDetector(channel).getEnergyBins()) #@UndefinedVariable
        values = self.ds[channel]
        
        result = plotNPeaks(energys,values,Gaussian,number_of_peaks_to_fit,smoothing)
        
        number_of_functions = result.getNoOfFunctions()
        
        peaks = []
        
        for i in range(number_of_functions):
            peaks += [result.getFunction(i).getParameterValue(0)]
            
        return peaks
    
    def removeNonMatchedPeaks(self,positions,threshold):
        # TODO might need to add in a check to pick up the closest value to a peak if
        # more than one peak is within the threshold
        newPositions = []
        for element in positions:
            if(element[1][0] < threshold):
                newPositions += [element]
                
        return newPositions
            
    
    def fitElement(self,channel, numberOfPeaks, numberOfMatchedPeaksRequired):
                
        print "fitting element %i" % channel
                
        peaks = self.fitPeaks(numberOfPeaks, 5, channel);
        
        # match peaks to calibrants
        positions = []
        for key in self.calibrants.iterkeys():
            positions += [(key,self.matchPeaks(peaks, key))]
            
        # now the peaks have been matched, remove all the non mached ones, over a threshold    
        
        tollerence = 1.0            
        cleanedPositions = self.removeNonMatchedPeaks(positions, tollerence)    
        
        while len(cleanedPositions) < numberOfMatchedPeaksRequired :
            print "only %d points available, so increasing tollerence" % len(cleanedPositions)
            tollerence += 0.2
            cleanedPositions = self.removeNonMatchedPeaks(positions, tollerence)
        
        # now produce a list of the binvalues, vrs q values
        binPositions = []
        qvalues = []
        
        energys = DataSet(edxd.getSubDetector(channel).getEnergyBins()) #@UndefinedVariable
        
        for element in cleanedPositions:
            binPositions += self.getEnergyBin(energys,element[1][2])
            qvalues += [self.calibrants[element[0]]]
        
        binPositions.sort()
        qvalues.sort()
        
        fit = Fitter.fit(DatasetFactory.createFromObject(binPositions),DatasetFactory.createFromObject(qvalues),GeneticAlg(0.00001),[Quadratic(-1,1,-1,1,-1,1)])
        
        # plot the result to show its a good fit
        RCPPlotter.plot("Plot 1",DatasetFactory.createFromObject(binPositions),[DatasetFactory.createFromObject(qvalues),fit.getFunction().makeDataSet([DatasetFactory.createFromObject(binPositions)])])
        
        # construct the q axis
        binAxis = DatasetFactory.createRange(edxd.getBins()) #@UndefinedVariable
        qAxis = fit.getFunction().makeDataSet([binAxis])
        
        # finally push this to the right location
        edxd.getSubDetector(channel).setQMapping(qAxis.doubleArray())    #@UndefinedVariable
            
        return fit
    
    def getEnergyBin(self,energys, energy):
        sfh = ScanFileHolder()
        return sfh.getInterpolatedX(DatasetFactory.createRange(len(energys)),energys,energy)
    
    def getPeakRatio(self,sortedPeaks, a,b,c):
        return (sortedPeaks[a]-sortedPeaks[b])/(sortedPeaks[a]-sortedPeaks[c])                        
    
                    
    def comparePeaksFromFile(self,filename,start, stop):
        self.loadOldData(filename)

        self.skeys = self.calibrants.keys()
        self.skeys.sort()
        
        qheader = self.calibrants.values()
        qheader.sort()
        
        print "EL %7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,chisquared" % tuple(qheader)
        
        for channel in range(start-1,stop-1) :
            self.peaks = self.fitPeaks(5, 5, channel)
            self.peaks.sort()
            #sleep(10)

            #find peaks at energies 45 and 73, and 86
            matchpeak = []
            matchpeak.append(self.matchPeaks(self.peaks, self.skeys[0]))
            matchpeak.append(self.matchPeaks(self.peaks, self.skeys[1]))
            matchpeak.append(self.matchPeaks(self.peaks, self.skeys[2]))

            #listprint(matchpeak)
            
            matchpeakvalues = []
            matchpeakvalues.append(self.peaks[matchpeak[0][1]])
            matchpeakvalues.append(self.peaks[matchpeak[1][1]])
            matchpeakvalues.append(self.peaks[matchpeak[2][1]])        
            
            
            # get the initial fit
            fit = Fitter.fit(DatasetFactory.createFromObject(self.skeys).getSlice([0],[3],[1]),DatasetFactory.createFromObject(matchpeakvalues).getSlice([0],[3],[1]),GeneticAlg(0.000001),[Quadratic(-1,1,-10,10,-100,100)])
                        
            # now the initial fit is made, the rest of the points can be found using this new conversion
            newMatchValues = fit.getFunction().makeDataSet([DatasetFactory.createFromObject(self.skeys)])
            newValues = newMatchValues.doubleArray().tolist()        
            
            # now refit all the peaks
            self.allpeaks = self.fitPeaks(50, 5, channel)
            
            # match peaks to calibrants
            positions = []
            for key in newValues:
                positions += [(key,self.matchPeaks(self.allpeaks, key))]
                
            # now the peaks have been matched, remove all the non mached ones, over a threshold    
            
            
            tollerence = 5
            
            self.chisquared = 1.0         

            while (self.chisquared > 0.0001) :
                        
                cleanedPositions = self.removeNonMatchedPeaks(positions, tollerence)
            
                #print "Values"
                #listprint(cleanedPositions)
            
                #usedpeaks = []                 
            
                # now produce a list of the binvalues, vrs q values
                self.binPositions = []
                self.qvalues = []
            
                energys = DataSet(edxd.getSubDetector(channel).getEnergyBins()) #@UndefinedVariable
            
                # for use later, in verification
                self.usedpeaks = []    
            
                for element in range(len(cleanedPositions)):
                    self.binPositions += self.getEnergyBin(energys,cleanedPositions[element][1][2])
                    self.qvalues += [self.calibrants[self.skeys[element]]]
                    self.usedpeaks += [cleanedPositions[element][1][1]]
            
                self.binPositions.sort()
                self.qvalues.sort()
                
                #print self.binPositions
                #print self.qvalues
                
                fit = Fitter.fit(DatasetFactory.createFromObject(self.binPositions),DatasetFactory.createFromObject(self.qvalues),GeneticAlg(0.000001),[Quadratic(-1,1,-2,2,-5,5)])
            
                # plot the result to show its a good fit
                RCPPlotter.plot("Plot 1",DatasetFactory.createFromObject(self.binPositions),[DatasetFactory.createFromObject(self.qvalues),fit.getFunction().makeDataSet([DatasetFactory.createFromObject(self.binPositions)])])
            
                # construct the q axis
                binAxis = DatasetFactory.createRange(edxd.getBins()) #@UndefinedVariable
                qAxis = fit.getFunction().makeDataSet([binAxis])
            
                # finally push this to the right location
            
                #print fit.disp()
                self.chisquared = fit.chiSquared
                tollerence = tollerence/2.0
                #print "Chisquared", self.chisquared, len(self.usedpeaks) 
            
            
            edxd.getSubDetector(channel).setQMapping(qAxis.doubleArray())                #@UndefinedVariable
            
            readback = plotNPeaks(qAxis,self.ds[channel],Gaussian,20,5)
    
            qpeaks = []
        
            for i in range(readback.getNoOfFunctions()):
                qpeaks += [readback.getFunction(i).getParameterValue(0)]
            
            
            # match peaks to calibrants
            qpositions = []
            qvalues = self.calibrants.values()
            qvalues.sort()
            for values in qvalues:
                tvalues = self.matchPeaks(qpeaks, values)
                if tvalues[1] in self.usedpeaks :
                    qpositions += [tvalues[0]]
                else :
                    qpositions += [-1.0]    
                
            print "%2i %7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f,%7.4f , %e" % tuple([channel+1]+qpositions+[self.chisquared])        
                
            # set the zero channel 
            edxd.getSubDetector(0).setQMapping(qAxis.doubleArray()) #@UndefinedVariable
                
            #print fit.disp()
            #print fit.chiSquared
            sleep(1)    
                        
        return
                        
    def fitElementsFromFile(self,filename):
        self.loadOldData(filename)
        
        print "File loaded sucsesfuly"
        
        for i in range(24):
            try :
                fit = self.fitElement(i,15,7)
                print "Chisquared = %f" % fit.getChiSquared()
                print "fit terms = %fx^2 + %fx + %f" % (fit.getFunction().getParameterValue(0),fit.getFunction().getParameterValue(1),fit.getFunction().getParameterValue(2))
                if(math.fabs(fit.getChiSquared()) > 0.001) :
                    print "!!!Bad fit found, reducing the number of needed points to try to get more consistancy"
                    fit = self.fitElement(i,5,3)
                    print "Chisquared = %f" % fit.getChiSquared()
                    print "fit terms = %fx^2 + %fx + %f" % (fit.getFunction().getParameterValue(0),fit.getFunction().getParameterValue(1),fit.getFunction().getParameterValue(2))
                    
            except :
                print "Element %i unsucsessfull" % i
                edxd.getSubDetector(i).setQMapping(DatasetFactory.createRange(edxd.getBins()).getData())    #@UndefinedVariable
                
            sleep(2)
            
            
    def initialiseQAxis(self):
        for i in range(24):
            energys = DataSet(edxd.getSubDetector(i).getEnergyBins()) #@UndefinedVariable
            edxd.getSubDetector(i).setQMapping(energys.doubleArray()) #@UndefinedVariable
            
    def setCalibrants(self, calibrants=[]):
        self.calibrants=calibrants
    
    def getCalibrants(self):
        return self.calibrants

