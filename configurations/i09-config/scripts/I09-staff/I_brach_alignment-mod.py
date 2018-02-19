Config=1

# Configuration 1: 2.5 keV focused
if Config==1:
    dcmenergy.moveTo(2.5)
    igap.asynchronousMoveTo(15.39)
    ienergy.setOrder(1)
    dcmoffset.asynchronousMoveTo(16)
    hs2ycentre.asynchronousMoveTo(15.7)
    
    dcmfpitch.asynchronousMoveTo(5)
    dcmfroll.asynchronousMoveTo(5)
#    pos dcmpitch 0.0496
#    pos dcmroll -0.0371
    
    pos dcmpitch 0.0521
    pos dcmroll -0.0385
    
    hd3iamp4.setGain("10^5 low noise")
    hd4iamp6.setGain("10^5 low noise")
    pos hm1pitch 0
    pos hm1x 1.5
    pos hd3x -20.595
#    pos hd3x -20.975
    pos hs1xgap 1.5
    scan dcmfpitch 0.5 9.5 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.532
#    pos hd4x -23.558
    pos hs1xgap 0.1
    rscan dcmfroll -2 2 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

# HM1
    pos hm1y -146.87
    pos hm1x 0.94
    pos hm1pitch 2.9
    pos hm1yaw 0.32
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1
    pos hm2x -1.2585
    pos hm2pitch 3.158
    
# CCC
    pos cccx -5

#HM3
    pos hm3y 5
    pos hm3pitch -0.4
    pos hm3x 1.395
    pos hm3mainbender 121000
    pos hm3elipticalbender 1190


# Configuration 2: 6 keV focused without any channel cuts
if Config==2:
    pos cccx -5
    pos igap 7.68
    ienergy.setOrder(5)
    pos dcmenergy 6
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0521
    pos dcmroll -0.07
    pos dcmroll -0.0385
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch -0.51
    pos hm1x 1.2
    pos hd3x -20.595
    pos hs1xgap 1.5
    rscan dcmfpitch -3 3 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.532
    pos hs1xgap 0.1
    rscan dcmfroll -2 2 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

# HM1
    pos hm1y -97.925
    pos hm1x 0.94
    pos hm1pitch 2.9
    pos hm1yaw 0.32
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1
    pos hm2x -1.2585
    pos hm2pitch 3.158

# CCC
    pos cccx -5

#HM3
    pos hm3y 5
    pos hm3pitch -0.45
    pos hm3x 0.826
    pos hm3mainbender 119500
    pos hm3elipticalbender 1190

# Configuration 3: Si(333) channel cut focused @ 5.9479 keV
if Config==3:
    pos igap 7.624
    pos dcmenergy 5.9479
    pos dcmoffset 18.49
    pos hs2ycentre 18.19
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0458
    pos dcmroll -0.0185
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch 0
    pos hm1x 1.5
    pos hd3x -20.975
    pos hs1xgap 1.5
    rscan dcmfpitch -3 3 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.558
    pos hs1xgap 0.1
    rscan dcmfroll -2 2.5 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

# HM1
    pos hm1y -95.855
    pos hm1x 0.475
    pos hm1pitch 3.0955
    pos hm1yaw 0.4
    pos hm1roll 0.02

# HM2
    pos hm2y 6.59
    pos hm2x -1.932
    pos hm2pitch 3.3412

# CCC
    pos cccy -130.81
#pos cccx 0.8

# HM3
    pos hm3x 1.445
    pos hm3pitch -0.4
    pos hm3mainbender 121000
    pos hm3elipticalbender 1190


# Configuration 4: Si(004) channel cut focused @ 5.9357 keV
if Config==4:
    pos igap 7.61
    pos dcmenergy 5.9343
    ienergy.setOrder(5)
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0521
    pos dcmroll -0.07
    pos dcmroll -0.0385
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch -0.51
    pos hm1x 1.2
    pos hd3x -20.595
    pos hs1xgap 1.5
    rscan dcmfpitch -3 3 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.532
    pos hs1xgap 0.1
    rscan dcmfroll -2 2 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

    pos dcmoffset 22.5
    pos hs2ycentre 22.2
# HM1
    pos hm1y -97.925+6.5
    pos hm1x 0.94
    pos hm1pitch 2.9
    pos hm1yaw 0.12
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1+6.5
    pos hm2x -1.2585
    pos hm2pitch 3.2

# CCC
    pos cccy -71
    pos cccx 4.23
    
# Check dcm energy
#    pos hd4x -31.558
#    scan dcmenergy 5.934 5.936 0.0001 hd4iamp6
#    pos dcmenergy peakdata.cfwhm
#    pos hd4x -1

# HM3
    pos hm3y 5
    pos hm3pitch -0.45
    pos hm3x 0.795
    pos hm3mainbender 119500
    pos hm3elipticalbender 1190

# Configuration 5: Si(044) channel cut focused @ 8.1417 keV
if Config==5:    
    pos cccx -5
    pos igap 7.47
    pos dcmenergy 8.1417
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0458
    pos dcmroll -0.0185
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch 0
    pos hm1x 1.5
    pos hd3x -20.975
    pos hs1xgap 1.5
    rscan dcmfpitch -3 3 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.558
    pos hs1xgap 0.1
    rscan dcmfroll -2 2.5 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

    pos dcmoffset 22.3
    pos hs2ycentre 22
# HM1
    pos hm1y -91.745
    pos hm1x 0.475
    pos hm1pitch 2.836
    pos hm1yaw 0.3
    pos hm1roll 0.02

# HM2
    pos hm2y 10.4
    pos hm2x -1.6522
    pos hm2pitch 3.116

# CCC
    pos cccy -10.5
    pos cccx 4.35

# HM3
    pos hm3x 1.4
    pos hm3pitch -0.4
    pos hm3mainbender 121000
    pos hm3elipticalbender 1190

# Configuration 6: 2.5 keV defocused in both directions
if Config==6:
#   pos igap 15.39
    ienergy.setOrder(1)
    pos ienergy 2.5
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos hs2ygap 2
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0506
    pos dcmroll -0.0193
    hd3iamp4.setGain("10^5 low noise")
    hd4iamp6.setGain("10^5 low noise")
    pos hm1pitch 0
    pos hm1x 1.5
    pos hd3x -20.975
    pos hs1xgap 1.5
    rscan dcmfpitch -4.5 4.5 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.558
    pos hs1xgap 0.1
    rscan dcmfroll -2 2 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

# HM1
    pos hm1y -146.87
    pos hm1x 1.985
    pos hm1pitch 6.4893
    pos hm1yaw -0.24
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1
    pos hm2x -4.838
    pos hm2pitch 6.64
    
# CCC
    pos cccx -5

#HM3
    pos hm3y 5
    pos hm3pitch -0.4
    pos hm3x 1.5636
    pos hm3mainbender 103000
    pos hm3elipticalbender 730

# Configuration 7: 2.5 keV defocused in vertical direction only
if Config==7:
#   pos igap 15.39
    ienergy.setOrder(1)
    pos ienergy 2.5
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos hs2ygap 2
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0506
    pos dcmroll -0.0193
    hd3iamp4.setGain("10^5 low noise")
    hd4iamp6.setGain("10^5 low noise")
    pos hm1pitch 0
    pos hm1x 1.5
    pos hd3x -20.975
    pos hs1xgap 1.5
    rscan dcmfpitch -4.5 4.5 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.558
    pos hs1xgap 0.1
    rscan dcmfroll -2 2 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

# HM1
    pos hm1y -146.87
    pos hm1x 1.985
    pos hm1pitch 6.4893
    pos hm1yaw -0.24
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1
    pos hm2x -4.838
    pos hm2pitch 6.64
    
# CCC
    pos cccx -5

#HM3
    pos hm3y 5
    pos hm3pitch -0.4
    pos hm3x 1.5636
    pos hm3mainbender 121000
    pos hm3elipticalbender 1190
