'''
create iSeg module channel voltage control scannables

Created on Oct 31, 2022

@author: fy65
'''
from detector.iseg_voltage_controller import ISegVoltageControl

dldv = ISegVoltageControl('dldv',3,0,pv_root="BL09K-EA-PSU-01:0"); dldv.configure()
mcp_b = ISegVoltageControl('mcp_b',2,0,pv_root="BL09K-EA-PSU-01:0"); mcp_b.configure()

def DLD_start(MCPB):
    dldv.moveTo(0)
    mcp_b.moveTo(0)
    
    dldv.on()
    mcp_b.on()
    
    dldv.setRampSpeed(1)
    
    dldv.moveTo(400)
    
    mcp_b.setRampSpeed(0.36)
    dldv.setRampSpeed(0.18)
    
    mcp_b.moveTo(MCPB)
    dldv.moveTo(MCPB+400)
    
def DLD_stop():
    mcp_b.setRampSpeed(0.36)
    dldv.setRampSpeed(0.18)

    mcp_b.moveTo(0)
    dldv.moveTo(400)

    dldv.setRampSpeed(1)
    
    dldv.moveTo(0)

    dldv.off()
    mcp_b.off()
    