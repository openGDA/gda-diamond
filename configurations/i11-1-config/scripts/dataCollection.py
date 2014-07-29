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

def collectData(stageName='ms1', calibrant='Si', calibrant_x=0, calibrant_y=0, calibrant_exposure=1.0, calibration_required=True, sample_x_start=0, sample_x_stop=1, sample_x_step=0.1, sample_y_start=None, sample_y_stop=None, sample_y_step=None, sample_exposure=1.0):
    stage=Finder.getInstance().find(stageName)
    pixium=Finder.getInstance().find('pixium_hdf')
    dummyScannable=DummyScannable("dummyScannable")
    additional_plugin_list = pixium.getAdditionalPluginList()[0]
    #Detector calibration
    if calibration_required:
        stage.x.moveTo(calibrant_x)
        stage.y.moveTo(calibrant_y)
        scan([dummyScannable, 1, 1, 1, pixium, calibrant_exposure])
        calibrant_file_name = additional_plugin_list.getFullFileName()
    builder = OSCommandRunnerBuilder.defaults()
    builder=builder.command([LocalProperties.get("org.opengda.lde.pixium.data.reduction.script","/dls_sw/apps/i11-scripts/bin/LDE-RunFromGDAAtEndOfScan.sh")])
    builder=builder.keepOutput(True)
    builder = builder.inputFilename(calibrant_file_name)
    builder = builder.outputFilename(os.path.splitext(calibrant_file_name)[0]+"_output.log")
    builder=builder.noTimeout()
    builder.build()

    # sample diffraction data
    args=[stage,sample_x_start,sample_x_stop,sample_x_step ]
    if sample_y_start is not None and sample_y_stop is not None and sample_y_stop is not None:
        args.append(sample_y_start)
        args.append(sample_y_stop)
        args.append(sample_y_step)
    args.append(sample_exposure)
    scan(args)
    sample_file_name = additional_plugin_list.getFullFileName()
    #builder = OSCommandRunnerBuilder.defaults()
    builder=builder.command([LocalProperties.get("org.opengda.lde.pixium.data.reduction.script","/dls_sw/apps/i11-scripts/bin/LDE-RunFromGDAAtEndOfScan.sh"),calibrant_file_name])
    builder=builder.keepOutput(True)
    builder = builder.inputFilename(sample_file_name)
    builder = builder.outputFilename(os.path.splitext(sample_file_name)[0]+"_output.log")
    builder=builder.noTimeout()
    builder.build()
