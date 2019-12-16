from BeamlineI07.devices.virtual6c import Virtual6CircleCompositeMotor
from gdaserver import diff1halpha, diff1valpha, diff1vgamma, diff1vdelta
from gda.configuration.properties import LocalProperties



diffmode = LocalProperties.get("gda.active.diffractometer.mode")

if diffmode == "eh1h":
	sgam = Virtual6CircleCompositeMotor('sgam', diff1halpha, diff1vgamma,  diff1vdelta, 'horizontalVirtualGamma')
	sdel = Virtual6CircleCompositeMotor('sdel', diff1halpha, diff1vgamma,  diff1vdelta, 'horizontalVirtualDelta')
elif diffmode == "eh1v":
	sgam = Virtual6CircleCompositeMotor('sgam', diff1valpha, diff1vgamma,  diff1vdelta, 'verticalVirtualGamma')
	sdel = Virtual6CircleCompositeMotor('sdel', diff1valpha, diff1vgamma,  diff1vdelta, 'verticalVirtualDelta')
elif diffmode == "eh2":
	sgam = Virtual6CircleCompositeMotor('sgam', diff2alpha, diff2gamma,  diff2delta, 'verticalVirtualGamma')
	sdel = Virtual6CircleCompositeMotor('sdel', diff2alpha, diff2gamma,  diff2delta, 'verticalVirtualDelta')



