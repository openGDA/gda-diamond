import scisoftpy as dnp

def s1_mrad_to_mm(mrad):
    s1_mm = mrad * 23.2575
    return mrad * 23.2575

def mm_to_mrad(size_mm,distance_m):
    return size_mm / distance_m

def laueBandwidth(mrad,Rm):
    return (mrad/1000) * 1

def calc_divergence():
    #start cameras
    #fully open s2 and s3
    
    #distances in m
    s1Dist = 23.2575
    laueDist = 26.640
    bpm1Dist = 30.394
    s2Dist = 30.599
    m1Dist = 31.773
    #bpm2 dist needs to be determined
    bpm2Dist = 33
    samDist = 35.6
    focusDist = 0
    
    #sizes in mm
    laueSizeX = float(caget("BL15J-AL-SLITS-01:X:CENTER.RBV")) * laueDist / s1Dist
    laueSizeY = float(caget("BL15J-AL-SLITS-01:Y:CENTER.RBV")) * laueDist / s1Dist
    
    m1SizeX = float(caget("BL15J-AL-SLITS-01:X:CENTER.RBV")) * m1Dist / s1Dist
    m1SizeY = float(caget("BL15J-AL-SLITS-01:Y:CENTER.RBV")) * m1Dist / s1Dist
    
    #bpm1SizeX = float(caget("BL15J-DI-BPM-01:STAT:SigmaX_RBV")) * 0.0218
    bpm1SizeX = 9
    bpm1SizeY = ((float(caget("BL15J-DI-BPM-01:STAT:SigmaY_RBV")) * 0.0217) - 0.1)/ 1.414213562
    
    #bpm2SizeX = float(caget("BL15J-DI-BPM-02:STAT:SigmaX_RBV")) * 0.0135
    bpm2SizeX = 3
    bpm2SizeY = ((float(caget("BL15J-DI-BPM-02:STAT:SigmaY_RBV")) * 0.0135) - 0.1)/ 1.414213562
    
    #divergenceX = float(dnp.arctan((bpm2SizeX - bpm1SizeX) / (bpm2Dist - bpm1Dist)))
    #divergenceY = float(dnp.arctan((bpm2SizeY - bpm1SizeY) / (bpm2Dist - bpm1Dist)))
    
    divergenceX = float(dnp.arctan((bpm1SizeX - bpm2SizeX) / ((samDist+focusDist-bpm1Dist)/1000 - (samDist+focusDist-bpm2Dist)/1000)))
    print divergenceX
    #focusSizeX = 0.7
    #focusSizeY = 0.02
    
print "test script loaded"