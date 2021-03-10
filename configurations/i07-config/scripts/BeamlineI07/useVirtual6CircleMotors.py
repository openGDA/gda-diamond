from BeamlineI07.devices.virtual6c import Virtual6CircleCompositeMotor
from gdaserver import diff1chi, diff1alpha, diff1gamma, diff1delta, diff2alpha, diff2gamma, diff2delta
from gda.configuration.properties import LocalProperties



diffmode = LocalProperties.get("gda.active.diffractometer.mode")

if diffmode == "eh1h":
	sgam = Virtual6CircleCompositeMotor('sgam', diff1chi, diff1gamma,  diff1delta, 'horizontalVirtualGamma')
	sdel = Virtual6CircleCompositeMotor('sdel', diff1chi, diff1gamma,  diff1delta, 'horizontalVirtualDelta')
elif diffmode == "eh1v":
	sgam = Virtual6CircleCompositeMotor('sgam', diff1alpha, diff1gamma,  diff1delta, 'verticalVirtualGamma')
	sdel = Virtual6CircleCompositeMotor('sdel', diff1alpha, diff1gamma,  diff1delta, 'verticalVirtualDelta')
elif diffmode == "eh2":
	sgam = Virtual6CircleCompositeMotor('sgam', diff2alpha, diff2gamma,  diff2delta, 'verticalVirtualGamma')
	sdel = Virtual6CircleCompositeMotor('sdel', diff2alpha, diff2gamma,  diff2delta, 'verticalVirtualDelta')



