from BeamlineParameters import JythonNameSpaceMapping, FinderNameMapping

from gda.scan import StaticScan
from uk.ac.gda.beans.exafs import XanesScanParameters
from gda.configuration.properties import LocalProperties
from gda.device import CounterTimer
from gda.device.detector.countertimer import CounterTimerBase
from gda.device.detector.xspress import XspressDetector
from gda.data.scan.datawriter import XasAsciiDataWriter, NexusExtraMetadataDataWriter
from gdascripts.messages.handle_messages import simpleLog

#from exafsscripts.exafs.i20_setup import setupI20, finishI20
from exafsscripts.exafs.configFluoDetector import configFluoDetector
from gda.jython.commands.ScannableCommands import scan, pos, add_default 
import string
from time import sleep
from gda.factory import Finder

from gda.data.scan.datawriter import NexusExtraMetadataDataWriter
from gda.data.scan.datawriter import NexusFileMetadata
from gda.data.scan.datawriter.NexusFileMetadata import EntryTypes, NXinstrumentSubTypes

def finish():
    pass
    

def setup(beanGroup):
    
    controller = None
    
    finder = Finder.getInstance()
    
    metadataActive = beanGroup.getOutput().isMetadataActive()
    if metadataActive:
        metadataList = beanGroup.getOutput().getMetadataList()
        for metadata in metadataList:
             from gda.data.scan.datawriter import AsciiMetadataConfig
             asciiConfig = AsciiMetadataConfig()
             asciiConfig.setLabel(metadata.getScannableName()+": %4.1f")
             asciiConfig.setLabelValues([finder.find(metadata.getScannableName())])
             header = finder.find("datawriterconfig").getHeader()
             header.add(asciiConfig)
             print "----- scannable added to metadata -----", metadata.getScannableName()
    
    
    jython_mapper = JythonNameSpaceMapping()
    sampleParameters = beanGroup.getSample()
    if sampleParameters.getStage() == "xythetastage":
        stageParameters = sampleParameters.getXYThetaStageParameters()
        targetPosition = [stageParameters.getX(), stageParameters.getY(), stageParameters.getTheta()]
        print "moving xythetastage (sam2) to ", targetPosition
        jython_mapper.sam2(targetPosition);
        print "xythetastage move complete."

    if sampleParameters.getStage() == "sxcryostage":
        stageParameters = sampleParameters.getSXCryoStageParameters()
        manual = stageParameters.isManual()
        if manual:
            targetPosition = [stageParameters.getHeight(), stageParameters.getRot()]
            print "moving sxcryostage (sam1) to ", targetPosition
            jython_mapper.sam1(targetPosition);
            print "sxcryostage move complete."
        else:
            sample = stageParameters.getSampleNumber()
            offset = stageParameters.getCalibHeight()
            heightTarget = offset + (float(sample-1)*15.5)
            jython_mapper.sam1y(heightTarget)
            rot = stageParameters.getRot()
            jython_mapper.sam1rot(rot)
            

    if sampleParameters.getTemperatureControl() != "None":
        if sampleParameters.getTemperatureControl() == "furnace":
            simpleLog("furnace is the temp controller")
            temp = sampleParameters.getFurnaceParameters().getTemperature()
            tolerance = sampleParameters.getFurnaceParameters().getTolerance()
            wait_time = sampleParameters.getFurnaceParameters().getTime()
            only_read = sampleParameters.getFurnaceParameters().isControlFlag()
            controller = jython_mapper.eurotherm
            
            meta = NexusFileMetadata("temp", jython_mapper.eurotherm(), EntryTypes.NXsample, NXinstrumentSubTypes.NXpositioner, "temp")
            NexusExtraMetadataDataWriter.removeMetadataEntry(meta)
            NexusExtraMetadataDataWriter.addMetadataEntry(meta)
            
            if only_read == False:
                simpleLog("controlling furnace")
                jython_mapper.eurotherm(temp);
                min = float(temp) - float(tolerance)
                max = float(temp) + float(tolerance)
                temp_final = False
                simpleLog("starting temperature control loop")
                
                while temp_final == False:
                    temp_readback = float(jython_mapper.eurotherm());
                    if temp_readback in range(min, max):
                        simpleLog("Temperature reached, checking if it has stabalised")
                        finalised = True;
                        time = 0;
                        while finalised == True and time < wait_time:
                            simpleLog("Temperature stable")
                            temp_readback = float(jython_mapper.eurotherm());
                            if (temp_readback in range(min, max)) == False:
                                simpleLog("Temperature unstable")
                                finalised = False
                            time += 1
                            sleep(1)
                        if finalised == True:
                            temp_final = True 
                    else:
                        simpleLog("Temperature = " + str(temp_readback))
                        sleep(1)
            
            
        if sampleParameters.getTemperatureControl() == "lakeshore":
            simpleLog("Lakeshore is the temp controller")
            
            selectTemp0 = sampleParameters.getLakeshoreParameters().isTempSelect0()
            selectTemp1 = sampleParameters.getLakeshoreParameters().isTempSelect1()
            selectTemp2 = sampleParameters.getLakeshoreParameters().isTempSelect2()
            selectTemp3 = sampleParameters.getLakeshoreParameters().isTempSelect3()
            
            temp = sampleParameters.getLakeshoreParameters().getSetPointSet()
            
            tolerance = sampleParameters.getLakeshoreParameters().getTolerance()
            wait_time = sampleParameters.getLakeshoreParameters().getTime()
            
            only_read = sampleParameters.getLakeshoreParameters().isControlFlag()
            
            
            if selectTemp0 == True:
                jython_mapper.lakeshore.setTempSelect(0);
            if selectTemp1 == True:
                jython_mapper.lakeshore.setTempSelect(1);
            if selectTemp2 == True:
                jython_mapper.lakeshore.setTempSelect(2);
            if selectTemp3 == True:
                jython_mapper.lakeshore.setTempSelect(3);
            
            jython_mapper.lakeshore.setExtraNames(["temp"])
            jython_mapper.lakeshore.setInputNames([])
            jython_mapper.lakeshore.setOutputFormat([u'%5.5g'])
            
            meta = NexusFileMetadata("temp", jython_mapper.lakeshore(), EntryTypes.NXsample, NXinstrumentSubTypes.NXpositioner, "temp")
            NexusExtraMetadataDataWriter.removeMetadataEntry(meta)
            NexusExtraMetadataDataWriter.addMetadataEntry(meta)
            
            if only_read == False:
                simpleLog("controlling lakeshore")
                if selectTemp0 == True:
                    jython_mapper.lakeshore.rawAsynchronousMoveTo([[0], temp]);
                if selectTemp1 == True:
                    jython_mapper.lakeshore.rawAsynchronousMoveTo([[1], temp]);
                if selectTemp2 == True:
                    jython_mapper.lakeshore.rawAsynchronousMoveTo([[2], temp]);
                if selectTemp3 == True:
                    jython_mapper.lakeshore.rawAsynchronousMoveTo([[3], temp]);
            
                min = float(temp) - float(tolerance)
                max = float(temp) + float(tolerance)
                temp_final = False
                simpleLog("starting temperature control loop")
                
                while temp_final == False:
                    temp_readback = float(jython_mapper.lakeshore());
                    if temp_readback in range(min, max):
                        simpleLog("Temperature reached, checking if it has stabalised")
                        finalised = True;
                        time = 0;
                        while finalised == True and time < wait_time:
                            simpleLog("Temperature stable")
                            temp_readback = float(jython_mapper.lakeshore());
                            if (temp_readback in range(min, max)) == False:
                                simpleLog("Temperature unstable")
                                finalised = False
                            time += 1
                            sleep(1)
                        if finalised == True:
                            temp_final = True 
                    else:
                        simpleLog("Temperature = " + str(temp_readback))
                        sleep(1)
                
            controller = jython_mapper.lakeshore

    if beanGroup.getDetector().getExperimentType() == "Fluorescence":
        configFluoDetector(beanGroup)
        
        sensitivity0 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[0].getChangeSensitivity()
        ion_chamber0 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[0].getName()
        gain0 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[0].getGain()
        
        sensitivity1 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[1].getChangeSensitivity()
        ion_chamber1 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[1].getName()
        gain1 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[1].getGain()
        
        sensitivity2 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[2].getChangeSensitivity()
        ion_chamber2 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[2].getName()
        gain2 = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()[2].getGain()
        
        if sensitivity0 == True:
            simpleLog("Setting ionc1 stanford")
            jython_mapper.ionc1_stanford(gain0)
            
        if sensitivity1 == True:
            simpleLog("Setting ionc2 stanford")
            jython_mapper.ionc2_stanford(gain1)
            
        if sensitivity2 == True:
            simpleLog("Setting ionc3 stanford")
            jython_mapper.ionc3_stanford(gain2)
        
        
        
        ionChambers = beanGroup.getDetector().getFluorescenceParameters().getIonChamberParameters()
        
        autoGas0 = ionChambers[0].getAutoFillGas()
        autoGas1 = ionChambers[1].getAutoFillGas()
        autoGas2 = ionChambers[2].getAutoFillGas()
        
        
        purge_pressure0 = "25.0"
        purge_period0 = "120.0"
        gas_fill1_pressure0 = str(ionChambers[0].getPressure()*1000.0)
        gas_fill1_period0 = str(ionChambers[0].getGas_fill1_period_box())
        gas_fill2_pressure0 = str(ionChambers[0].getTotalPressure()*1000.0)
        gas_fill2_period0 = str(ionChambers[0].getGas_fill2_period_box())
        gas_select_val0 = "0"
        flushString0 = str(ionChambers[0].getFlush())
        
        purge_pressure1 = "25.0"
        purge_period1 = "120.0"
        gas_fill1_pressure1 = str(ionChambers[1].getPressure()*1000.0)
        gas_fill1_period1 = str(ionChambers[1].getGas_fill1_period_box())
        gas_fill2_pressure1 = str(ionChambers[1].getTotalPressure()*1000.0)
        gas_fill2_period1 = str(ionChambers[1].getGas_fill2_period_box())
        gas_select_val1 = "1"
        flushString1 = str(ionChambers[1].getFlush())
        
        purge_pressure2 = "25.0";
        purge_period2 = "120.0"
        gas_fill1_pressure2 = str(ionChambers[2].getPressure()*1000.0)
        gas_fill1_period2 = str(ionChambers[2].getGas_fill1_period_box())
        gas_fill2_pressure2 = str(ionChambers[2].getTotalPressure()*1000.0)
        gas_fill2_period2 = str(ionChambers[2].getGas_fill2_period_box())
        gas_select_val2 = "2"
        flushString2 = str(ionChambers[2].getFlush())
        
        if autoGas0 == True:
            jython_mapper.ionc1_gas_injector([purge_pressure0, purge_period0, gas_fill1_pressure0, gas_fill1_period0, gas_fill2_pressure0, gas_fill2_period0, gas_select_val0, flushString0])
        if autoGas1 == True:
            jython_mapper.ionc2_gas_injector([purge_pressure1, purge_period1, gas_fill1_pressure1, gas_fill1_period1, gas_fill2_pressure1, gas_fill2_period1, gas_select_val1, flushString1])
        if autoGas2 == True:
            jython_mapper.ionc3_gas_injector([purge_pressure2, purge_period2, gas_fill1_pressure2, gas_fill1_period2, gas_fill2_pressure2, gas_fill2_period2, gas_select_val2, flushString2])

        
        if beanGroup.getDetector().getFluorescenceParameters().isCollectDiffractionImages():
            # XasAsciiDataWriter.setBeanGroup(beanGroup) should have already been called to ensure the 
            # MythenXasImpl writes to the correct directory

            #move the DCM to required energy
            print "Moving DCM..."
            energy = jython_mapper.energy
            energyForMythen = beanGroup.getDetector().getFluorescenceParameters().getMythenEnergy()
            energy(energyForMythen)

            print "Collecting a diffraction image..."
            # drive the mythen
            mythen = jython_mapper.mythen
            collectionTime = beanGroup.getDetector().getFluorescenceParameters().getMythenTime()
            mythen.setCollectionTime(collectionTime)
            staticscan = StaticScan([mythen])
            staticscan.run()
            print "Diffraction scan complete."
             
            # call setBeanGroup again to ensure the settings are retained for the actual data collection
            XasAsciiDataWriter.setBeanGroup(beanGroup)
    
    if beanGroup.getDetector().getExperimentType() == "Transmission":
        #configFluoDetector(beanGroup)
        
        sensitivity0 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[0].getChangeSensitivity()
        ion_chamber0 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[0].getName()
        gain0 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[0].getGain()
        
        sensitivity1 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[1].getChangeSensitivity()
        ion_chamber1 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[1].getName()
        gain1 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[1].getGain()
        
        sensitivity2 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[2].getChangeSensitivity()
        ion_chamber2 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[2].getName()
        gain2 = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()[2].getGain()
        
        if sensitivity0 == True:
            simpleLog("Setting ionc1 stanford")
            jython_mapper.ionc1_stanford(gain0)
            
        if sensitivity1 == True:
            simpleLog("Setting ionc2 stanford")
            jython_mapper.ionc2_stanford(gain1)
            
        if sensitivity2 == True:
            simpleLog("Setting ionc3 stanford")
            jython_mapper.ionc3_stanford(gain2)
        
        ionChambers = beanGroup.getDetector().getTransmissionParameters().getIonChamberParameters()
        
        autoGas0 = ionChambers[0].getAutoFillGas()
        autoGas1 = ionChambers[1].getAutoFillGas()
        autoGas2 = ionChambers[2].getAutoFillGas()
        
        purge_pressure0 = "25.0"
        purge_period0 = "120.0"
        gas_fill1_pressure0 = str(ionChambers[0].getPressure()*1000.0)
        gas_fill1_period0 = str(ionChambers[0].getGas_fill1_period_box())
        gas_fill2_pressure0 = str(ionChambers[0].getTotalPressure()*1000.0)
        gas_fill2_period0 = str(ionChambers[0].getGas_fill2_period_box())
        gas_select_val0 = "0"
        flushString0 = str(ionChambers[0].getFlush())
        
        purge_pressure1 = "25.0"
        purge_period1 = "120.0"
        gas_fill1_pressure1 = str(ionChambers[1].getPressure()*1000.0)
        gas_fill1_period1 = str(ionChambers[1].getGas_fill1_period_box())
        gas_fill2_pressure1 = str(ionChambers[1].getTotalPressure()*1000.0)
        gas_fill2_period1 = str(ionChambers[1].getGas_fill2_period_box())
        gas_select_val1 = "1"
        flushString1 = str(ionChambers[1].getFlush())
        
        purge_pressure2 = "25.0";
        purge_period2 = "120.0"
        gas_fill1_pressure2 = str(ionChambers[2].getPressure()*1000.0)
        gas_fill1_period2 = str(ionChambers[2].getGas_fill1_period_box())
        gas_fill2_pressure2 = str(ionChambers[2].getTotalPressure()*1000.0)
        gas_fill2_period2 = str(ionChambers[2].getGas_fill2_period_box())
        gas_select_val2 = "2"
        flushString2 = str(ionChambers[2].getFlush())
        
        if autoGas0 == True:
            jython_mapper.ionc1_gas_injector([purge_pressure0, purge_period0, gas_fill1_pressure0, gas_fill1_period0, gas_fill2_pressure0, gas_fill2_period0, gas_select_val0, flushString0])
        if autoGas1 == True:
            jython_mapper.ionc2_gas_injector([purge_pressure1, purge_period1, gas_fill1_pressure1, gas_fill1_period1, gas_fill2_pressure1, gas_fill2_period1, gas_select_val1, flushString1])
        if autoGas2 == True:
            jython_mapper.ionc3_gas_injector([purge_pressure2, purge_period2, gas_fill1_pressure2, gas_fill1_period2, gas_fill2_pressure2, gas_fill2_period2, gas_select_val2, flushString2])

        
        
        if beanGroup.getDetector().getTransmissionParameters().isCollectDiffractionImages():
            # XasAsciiDataWriter.setBeanGroup(beanGroup) should have already been called to ensure the 
            # MythenXasImpl writes to the correct directory

            #move the DCM to required energy
            print "Moving DCM..."
            energy = jython_mapper.energy
            energyForMythen = beanGroup.getDetector().getTransmissionParameters().getMythenEnergy()
            energy(energyForMythen)

            print "Collecting a diffraction image..."
            # drive the mythen
            mythen = jython_mapper.mythen
            collectionTime = beanGroup.getDetector().getTransmissionParameters().getMythenTime()
            mythen.setCollectionTime(collectionTime)
            staticscan = StaticScan([mythen])
            staticscan.run()
            print "Diffraction scan complete."
             
            # call setBeanGroup again to ensure the settings are retained for the actual data collection
            XasAsciiDataWriter.setBeanGroup(beanGroup)
    
    return controller