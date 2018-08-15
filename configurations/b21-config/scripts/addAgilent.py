aw=gda.device.scannable.AgilentWaveform("aw", "172.23.122.129")
aw.configure()
aw.getPosition()
# mode SIN, RAMP, SIN, SQU, RAMP, PULS, NOIS, DC, USER
# frequency (Hz)
# amplitude (VPP)
# offset (V)
##aw(["SIN", 50, 1, 0.05])
# ramp from 1Hz to 10MHz in 15 log steps
##for i in range(15):
##	time.sleep(1)
##	aw.asynchronousMoveTo(["SIN", 10**(i/2.0), 1, 0])
##	# ncddetectors collection here
