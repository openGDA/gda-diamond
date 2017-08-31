'''
Created on 29 Aug 2017

@author: fy65
'''
from scannabledevices.samplePositioner import SamplePositioner
from scannabledevices.positionerValue import PositionerValue, DummyPositionerValue
from __main__ import smplXPositioner,smplYPositioner,smplZPositioner,smplRZPositioner,smplTiltPositioner,smplAzimuthPositioner,m5tthPositioner,smplDiodetthPositioner,sax,say,saz,sapolar,satilt,saazimuth,m5tth,diodetth  # @UnresolvedImport
import installation

if installation.isLive():
    xval = PositionerValue("xval", smplXPositioner, "BL21I-EA-SMPL-01:MTP:X")  
    yval = PositionerValue("yval", smplYPositioner, "BL21I-EA-SMPL-01:MTP:Y")  
    zval = PositionerValue("zval", smplZPositioner, "BL21I-EA-SMPL-01:MTP:Z")  
    polarval = PositionerValue("polarval", smplRZPositioner, "BL21I-EA-SMPL-01:MTP:RZ")  
    tiltval = PositionerValue("tiltval", smplTiltPositioner, "BL21I-EA-SMPL-01:MTP:TILT")  
    azimval = PositionerValue("azimval", smplAzimuthPositioner, "BL21I-EA-SMPL-01:MTP:AZIM")  
    m5rotval = PositionerValue("m5rotval", m5tthPositioner, "BL21I-MO-POD-02:MTP:ROT")  
    diodetthval = PositionerValue("diodetthval", smplDiodetthPositioner, "BL21I-EA-SMPL-01:MTP:DRING")  
else:
    xval = DummyPositionerValue("xval", smplXPositioner, sax, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    yval = DummyPositionerValue("yval", smplYPositioner, say, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    zval = DummyPositionerValue("zval", smplZPositioner, saz, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    polarval = DummyPositionerValue("polarval", smplRZPositioner, sapolar, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    tiltval = DummyPositionerValue("tiltval", smplTiltPositioner, satilt, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    azimval = DummyPositionerValue("azimval", smplAzimuthPositioner, saazimuth, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    m5rotval = DummyPositionerValue("m5rotval", m5tthPositioner, m5tth, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    diodetthval = DummyPositionerValue("diodetthval", smplDiodetthPositioner, diodetth, positions={"Screws":1.0, "Transfer":2.0, "RIXS": 3.0})  
    
smp_positioner = SamplePositioner("smp_positioner",
                                smplXPositioner, smplYPositioner, smplZPositioner, smplRZPositioner, smplTiltPositioner, smplAzimuthPositioner, m5tthPositioner, smplDiodetthPositioner,  
                                sax, say, saz, sapolar, satilt, saazimuth, m5tth, diodetth,  
                                xval, yval, zval, polarval, tiltval, azimval, m5rotval, diodetthval, tolerance=0.001)

if __name__ == '__main__':
    pass
