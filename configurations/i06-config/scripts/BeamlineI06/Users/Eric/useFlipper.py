from Diamond.PseudoDevices.FlippingDevice import FlippingDeviceClass, Algorism01Processor;


#The following example demos how to:
#
# scan the energy from 500 to 700. At each point, flip the dac11 at -10V and +10V respectively and measure ca61sr and ca62sr
#
# Output
#	v0 = ca61sr/ca63sr at +10V
#	v1 = ca61sr/ca63sr at -10V
#	val = (v0-v1) / (v0+v1)


scannerName = "pgmenergy";
flipperName = "dac11";
detectorNames = ["ca61sr", "ca63sr"]
integrationTime = 0.5

fenergy = FlippingDeviceClass('fenergy', scannerName, flipperName, [10, -10], detectorNames, integrationTime, [Algorism01Processor()]);


#scan flippedEnergy 500 700 0.1

