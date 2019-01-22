'''
Created on 29 Aug 2017

@author: fy65
'''
from scannabledevices.samplePositioner import SamplePositioner
from scannabledevices.positionerValue import PositionerValue, DummyPositionerValue
from __main__ import smplXPositioner,smplYPositioner,smplZPositioner,smplRZPositioner,smplTiltPositioner,smplAzimuthPositioner,m5tthPositioner,smplDiodetthPositioner,x,y,z,th,chi,phi,m5tth,difftth  # @UnresolvedImport
import installation

if installation.isLive():
    xval = PositionerValue("xval", smplXPositioner, "BL21I-EA-SMPL-01:MTP:X")  
    yval = PositionerValue("yval", smplYPositioner, "BL21I-EA-SMPL-01:MTP:Y")  
    zval = PositionerValue("zval", smplZPositioner, "BL21I-EA-SMPL-01:MTP:Z")  
    thval = PositionerValue("thval", smplRZPositioner, "BL21I-EA-SMPL-01:MTP:RZ")  
    chival = PositionerValue("chival", smplTiltPositioner, "BL21I-EA-SMPL-01:MTP:TILT")  
    phival = PositionerValue("phival", smplAzimuthPositioner, "BL21I-EA-SMPL-01:MTP:AZIM")  
    m5rotval = PositionerValue("m5rotval", m5tthPositioner, "BL21I-MO-POD-02:MTP:ROT")  
    difftthval = PositionerValue("difftthval", smplDiodetthPositioner, "BL21I-EA-SMPL-01:MTP:DRING")  
else:
    xval = DummyPositionerValue("xval", smplXPositioner, x, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    yval = DummyPositionerValue("yval", smplYPositioner, y, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    zval = DummyPositionerValue("zval", smplZPositioner, z, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    thval = DummyPositionerValue("thval", smplRZPositioner, th, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    chival = DummyPositionerValue("chival", smplTiltPositioner, chi, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    phival = DummyPositionerValue("phival", smplAzimuthPositioner, phi, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    m5rotval = DummyPositionerValue("m5rotval", m5tthPositioner, m5tth, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    difftthval = DummyPositionerValue("difftthval", smplDiodetthPositioner, difftth, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    
smp_positioner = SamplePositioner("smp_positioner",
                                smplXPositioner, smplYPositioner, smplZPositioner, smplRZPositioner, smplTiltPositioner, smplAzimuthPositioner, m5tthPositioner, smplDiodetthPositioner,  
                                x, y, z, th, chi, phi, m5tth, difftth,  
                                xval, yval, zval, thval, chival, phival, m5rotval, difftthval, tolerance=0.001)

if __name__ == '__main__':
    pass
