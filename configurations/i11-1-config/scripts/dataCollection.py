'''
Created on 28 Jul 2014

@author: fy65
'''
from gda.factory import Finder
from gda.device.scannable import DummyScannable
from gda.jython.commands.ScannableCommands import scan
from gda.util import OSCommandRunnerBuilder
from gda.configuration.properties import LocalProperties
import os
from LookupTables import readLookupTable
from gda.jython import InterfaceProvider

class StageDataCollection:
    def __init__(self, stageName):
        self.name=stageName
        self.calibrant_file_name=None
        self.stage_x=Finder.getInstance().find(stageName+"x")
        self.stage_y=Finder.getInstance().find(stageName+"y")
        self.stage_rot=Finder.getInstance().find(stageName+"rot")
        self.lookup_table = readLookupTable(LocalProperties.get("gda.function.lookupTable.dir")+os.path.sep+"lde_stages_home_positions.txt")
        self.samples=[]
        self.calibration_required=True
        self.pixium=Finder.getInstance().find('pixium_hdf')

    def addSample(self, sample={}):
        self.samples.append(sample)
        
    def removeSample(self, sample={}):
        self.samples.remove(sample)
        
    def moveDetectorToPosition(self, pixium_x=None, pixium_y=None, pixium_z=None):
        if self.isDetectorAtPosition(pixium_z):
            #TODO: do I need to check X and Y positionS?
            self.calibration_required=False
        else:
            if pixium_x is not None:
                pixium_arm_x.moveTo(pixium_x)  # @UndefinedVariable
            if pixium_y is not None:
                pixium_arm_y.moveTo(pixium_y)  # @UndefinedVariable
            if pixium_z is not None:
                pixium_arm_z.moveTo(pixium_z)  # @UndefinedVariable
            self.calibration_required=True
        
    def doCalibration(self, calibrant='Si', calibrant_x=0, calibrant_y=0, calibrant_exposure=1.0):
        if self.calibration_required:
            mycalibrant=Finder.getInstance().find("calibrant_name")
            mycalibrant.moveTo(calibrant)
            
            dummyScannable=DummyScannable("dummyScannable")
            
            #additional_plugin_list = pixium.getAdditionalPluginList()[0]
            #Detector calibration
            if self.calibration_required:
                self.stage_x.moveTo(calibrant_x)
                self.stage_y.moveTo(calibrant_y)
                scan([dummyScannable, 1, 1, 1, self.pixium, calibrant_exposure])
                #TODO GDA .nxs file, not EPICS h5 file
                scan_data_point_provider = InterfaceProvider.getScanDataPointProvider()
                self.calibrant_file_name = scan_data_point_provider.getLastScanDataPoint().getCurrentFilename()
                #calibrant_file_name = additional_plugin_list.getFullFileName()
                #do detector calibration on cluster serevrs
                builder = OSCommandRunnerBuilder.defaults()
                builder=builder.command([LocalProperties.get("org.opengda.lde.pixium.data.reduction.script","/dls_sw/apps/i11-scripts/bin/LDE-RunFromGDAAtEndOfScan.sh")])
                builder=builder.keepOutput(True)
                builder = builder.inputFilename(self.calibrant_file_name)
                builder = builder.outputFilename(os.path.splitext(self.calibrant_file_name)[0]+"_output.log")
                builder=builder.noTimeout()
                builder.build()
                self.calibration_required=False
            
    def processSamples(self):
        if self.samples.count!=0:
            for sample in self.samples:
                self.moveDetectorToPosition(sample["pixium_x"], sample["pixium_y"], sample["pixium_z"])
                self.doCalibration(sample["calibrant"], sample["calibrant_x"], sample["calibrant_y"], sample["calibrant_exposure"])
                self.doSampleDataCollection(sample["sample_x_start"], sample["sample_x_stop"], sample["sample_x_step"], sample["sample_y_start"], sample["sample_y_stop"], sample["sample_y_step"], sample["sample_exposure"])
        self.moveToEngagedPosition()
        
    def doSampleDataCollection(self, sample_x_start=None, sample_x_stop=None, sample_x_step=None, sample_y_start=None, sample_y_stop=None, sample_y_step=None, sample_exposure=1.0):
        # sample diffraction data
        args=[]
        
        if sample_x_start is not None or sample_x_stop is not None or sample_x_step is not None:
            args.append(self.stage_x)
        if sample_y_start is not None:
            args.append(sample_x_start)
        if sample_y_stop is not None:
            args.append(sample_x_stop)
        if sample_y_step is not None:
            args.append(sample_x_step)
        
        if sample_y_start is not None or sample_y_stop is not None or sample_y_step is not None:
            args.append(self.stage_y)
        if sample_y_start is not None:
            args.append(sample_y_start)
        if sample_y_stop is not None:
            args.append(sample_y_stop)
        if sample_y_step is not None:
            args.append(sample_y_step)
        if args.count!=0:
            args.append(self.pixium)
            args.append(sample_exposure)
        scan(args)
        #sample_file_name = additional_plugin_list.getFullFileName()
        scan_data_point_provider = InterfaceProvider.getScanDataPointProvider()
        sample_file_name = scan_data_point_provider.getLastScanDataPoint().getCurrentFilename()
        #builder = OSCommandRunnerBuilder.defaults()
        builder = OSCommandRunnerBuilder.defaults()
        builder=builder.command([LocalProperties.get("org.opengda.lde.pixium.data.reduction.script","/dls_sw/apps/i11-scripts/bin/LDE-RunFromGDAAtEndOfScan.sh"),self.calibrant_file_name])
        builder=builder.keepOutput(True)
        builder = builder.inputFilename(sample_file_name)
        builder = builder.outputFilename(os.path.splitext(sample_file_name)[0]+"_output.log")
        builder=builder.noTimeout()
        builder.build()
    
    def moveToEngagedPosition(self):
        self.stage_x.moveTo(float(self.lookup_table[self.name.upper()][2]))
        
    def moveToSafePosition(self):
        self.stage_x.moveTo(float(self.lookup_table[self.name.upper()][0]))
        self.stage_y.moveTo(float(self.lookup_table[self.name.upper()][1]))
        #self.stage_rot.moveTo(lookup_table[stageName.upper()][2])
            
    def isAtSafePosition(self):
        #TODO: require Tolerance value here
        return float(self.stage_x.getPosition())==float(self.lookup_table[self.name.upper()][0]) and float(self.stage_y.getPosition())==float(self.lookup_table[self.name.upper()][1])
    
    def isDetectorAtPosition(self, pixium_z):
        #TODO: need motor Tolerance data here
        return pixium_z is not None and float(pixium_arm_z.getPosition()==float(pixium_z))  # @UndefinedVariable
                
    def getName(self):
        return self.name
    def setName(self, name):
        self.name=name
        
stagedatacollection=StageDataCollection("MS1")
collectDiffractionData=stagedatacollection.processSamples()
moveToSafePosition=stagedatacollection.moveToSafePosition

from gda.jython.commands.GeneralCommands import alias 
alias("collectDiffractionData")
alias("moveToSafePosition")

def createSampleDict(name, cellID, visitID, calibrant='Si', calibrant_x=0, calibrant_y=0, calibrant_exposure=1.0, sample_x_start=None, sample_x_stop=None, sample_x_step=None, sample_y_start=None, sample_y_stop=None, sample_y_step=None, sample_exposure=1.0, pixium_x=None, pixium_y=None, pixium_z=None ):
    sample={}
    sample["name"]=name
    sample["cell_ID"]=cellID
    sample["visit_ID"]=visitID
    sample["calibrant"]=calibrant
    sample["calibrant_x"]=calibrant_x
    sample["calibrant_y"]=calibrant_y
    sample["calibrant_exposure"]=calibrant_exposure
    sample["sample_x_start"]=sample_x_start
    sample["sample_x_stop"]=sample_x_stop
    sample["sample_x_step"]=sample_x_step
    sample["sample_y_start"]=sample_y_start
    sample["sample_y_stop"]=sample_y_stop
    sample["sample_y_step"]=sample_y_step
    sample["sample_exposure"]=sample_exposure
    sample["pixium_x"]=pixium_x
    sample["pixium_y"]=pixium_y
    sample["pixium_z"]=pixium_z
    return sample
    
def parkingAllDevices():
    '''move all stages to parking positions'''
    lookuptable=readLookupTable(LocalProperties.get("gda.function.lookupTable.dir")+os.path.sep+"lde_stages_home_positions.txt")
    for each in lookuptable.keys:
        stage=StageDataCollection(each)
        stage.moveToSafePosition()
alias("parkingAllDevices")

def dataCollection(samples=[]):
    lookuptable=readLookupTable(LocalProperties.get("gda.function.lookupTable.dir")+os.path.sep+"lde_stages_home_positions.txt")
    
    for each in lookuptable.keys:
        stage=StageDataCollection(each)
        for sample in samples:
            if sample["cell_ID"].contains(each):
                stage.addSample(sample)
        stage.processSamples()