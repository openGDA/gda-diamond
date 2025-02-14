'''
create iSeg module channel voltage control scannables

Created on Oct 31, 2022

@author: fy65
'''
from detector.iseg_voltage_controller import ISegVoltageControl
from detector.total_image_count import IntegratedSpectrum
from gdascripts.utils import caput

dldv = ISegVoltageControl('dldv',3,7,pv_root="BL09K-EA-PSU-01:0", tolerance = 1.0, ramp_speed = 1.0); dldv.configure()
mcp_b = ISegVoltageControl('mcp_b',7,1,pv_root="BL09K-EA-PSU-01:0", tolerance = 1.0, ramp_speed = 1.0); mcp_b.configure()
#kenergy = ISegVoltageControl('kenergy',5,3,pv_root="BL09K-EA-PSU-01:0", tolerance = 0.01, ramp_speed = 4.0); kenergy.configure() #for sample biasing with 500 V module
kenergy = ISegVoltageControl('kenergy',7,4,pv_root="BL09K-EA-PSU-01:0", tolerance = 0.04, ramp_speed = 1.0); kenergy.configure() #for sample biasing with 4000 V module
#kenergy = ISegVoltageControl('kenergy',6,4,pv_root="BL09K-EA-PSU-01:0", tolerance = 0.04, ramp_speed = 1.0); kenergy.configure() #for sample biasing with 2000 V module
focus = ISegVoltageControl('focus',3,0,pv_root="BL09K-EA-PSU-01:0", tolerance = 1, ramp_speed = 1.0); focus.configure()
testPS = ISegVoltageControl('testPS',7,0,pv_root="BL09K-EA-PSU-01:0", tolerance = .2, ramp_speed = 1.0); testPS.configure()
int_spec = IntegratedSpectrum("int_spec", "BL09K-EA-D-01:")

#caput("BL09K-EA-D-01:Stats1:NDArrayPort", "ROI1")
'''Sample_IRamp=EpicsReadWritePVClass("Sample_IRamp","BL09K-EA-PSU-01:0:1:CurrentRampSpeed","%/s*I_nom","%f")'''

def DLD_start(U_DLD):
		dldv.rawAsynchronousMoveTo(0)
		mcp_b.rawAsynchronousMoveTo(0)

		mcp_b.waitWhileBusy()
		dldv.waitWhileBusy()

		dldv.on()
		mcp_b.on()

		dldv.setRampSpeed(1)

		dldv.rawAsynchronousMoveTo(400)

		dldv.waitWhileBusy()

		mcp_b.setRampSpeed(0.5)
		dldv.setRampSpeed(0.5)

		mcp_b.rawAsynchronousMoveTo(U_DLD-400)
		dldv.rawAsynchronousMoveTo(U_DLD)

		mcp_b.waitWhileBusy()
		dldv.waitWhileBusy()

def DLD_stop():
		mcp_b.setRampSpeed(0.5)
		dldv.setRampSpeed(0.5)

		mcp_b.rawAsynchronousMoveTo(0)
		dldv.rawAsynchronousMoveTo(400)

		mcp_b.waitWhileBusy()
		dldv.waitWhileBusy()

		dldv.setRampSpeed(1)

		dldv.rawAsynchronousMoveTo(0)

		dldv.waitWhileBusy()

		dldv.off()
		mcp_b.off()

def DLDonly_start(MCPB): ## DLD current voltage 2300
		dldv.rawAsynchronousMoveTo(0)

		dldv.waitWhileBusy()

		dldv.on()

		dldv.setRampSpeed(0.5)
		# after venting use 0.18
		#dldv.setRampSpeed(0.18)


		dldv.rawAsynchronousMoveTo(MCPB)

		dldv.waitWhileBusy()

def DLDonly_stop():
		dldv.setRampSpeed(0.5)
		# after venting use 0.18
		#dldv.setRampSpeed(0.18)

		dldv.rawAsynchronousMoveTo(0)

		dldv.waitWhileBusy()

		dldv.off()


# save_tiff=EpicsReadWritePVClass("save_tiff","BL09K-EA-D-01:TIFF1:WriteFile","V","%i")
# save_filename =EpicsReadWritePVClass("save_filename","BL09K-EA-D-01:TIFF1:FileName","V","%t")
# Acquire = EpicsReadWritePVClass("Acquire","BL09K-EA-D-01:cam1:Acquire","V","%i")
# Exposure = EpicsReadWritePVClass("Exposure","BL09K-EA-D-01:cam1:AcquireTime","V","%f")
# Clear_data = EpicsReadWritePVClass("Clear_data","BL09K-EA-D-01:cam1:ZeroCube","V","%i")

# def runScan(start, stop, step, Exp_time):
#     Nstep = int((stop-start)/step+1)
#     pos Exposure Exp_time
#     for i in range(0, Nstep):
#         sample_bias.rawAsynchronousMoveTo(start+i*step)
#         pos Clear_data 1.0
#         pos Acquire 1.0
#         sleep(Exp_time + 1.0)
#         pos save_tiff 1.0
#     pos Acquire 0.0

