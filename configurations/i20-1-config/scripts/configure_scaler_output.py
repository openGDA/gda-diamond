from gda.device.detector.countertimer import ScalerOutputProcessor

configForLogI0It = [ 
        ScalerOutputProcessor.OutputConfig("I0", "%.4f", 1), 
        ScalerOutputProcessor.OutputConfig("It", "%.4f", 2),
        ScalerOutputProcessor.OutputConfig("lnI0It", "%.4f", 1, 2, 2) 
        ]

configForFFI0 = [ 
        ScalerOutputProcessor.OutputConfig("FF", "%.4f", 2),
        ScalerOutputProcessor.OutputConfig("FFI0", "%.4f", 2, 1, 1),
        ScalerOutputProcessor.OutputConfig("I0", "%.4f", 1)
        ]


#Set name of time frame (default is 'time')
scaler_for_zebra.getScalerOutputProcessor().setTimeChannelName("frame_time");
scaler_for_zebra.setTimeChannelRequired(True)

# set the config for the output format
# scaler_for_zebra.setScalerOutputConfig( mapToJava(configForFFI0) ) 
scaler_for_zebra.setScalerOutputConfig( mapToJava(configForLogI0It) ) 

# set readout to use new format
scaler_for_zebra.setUseCustomisedOutput(True) 