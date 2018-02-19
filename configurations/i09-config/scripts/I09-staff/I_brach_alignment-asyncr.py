Config=5

# Configuration 1: 2.5 keV focused
if Config==1:
    pos igap 15.415
    pos dcmenergy 2.5
    ienergy.setOrder(1)
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0521
    pos dcmroll -0.07
    pos dcmroll -0.0385
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch -0.41
    pos hm1x 2
    pos hd3x -20.595
    pos hs1xgap 1.5
    rscan dcmfpitch -4.5 4.5 0.1 hd3iamp4
    pos dcmfpitch peakdata.cfwhm
    pos hd3x -1
    pos hd4x -23.532
    pos hs1xgap 0.1
    pos cccx -5
    rscan dcmfroll -2 2 0.05 hd4iamp6
    pos dcmfroll peakdata.cfwhm
    pos hd4x -1
    pos hs1xgap 1.5

# HM1
    pos hm1y -146.87
    pos hm1x 2.467
    pos hm1pitch 4.826
    pos hm1yaw -0.3
    pos hm1roll 0.02

# HM2
    pos hm2y 4.1
    pos hm2x -2.64
    pos hm2pitch 5.04
    
#HM3
    pos hm3y 4.8915
    pos hm3pitch -0.4
    pos hm3x 1.275
    pos hm3mainbender 120000
    pos hm3elipticalbender 1190


# Configuration 2: 6 keV focused without any channel cuts
if Config==2:
    pos cccx -5
#    pos igap 7.68
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
    pos hm3y 4.8915
    pos hm3pitch -0.45
    pos hm3x 0.826
    pos hm3mainbender 119500
    pos hm3elipticalbender 1190

# Configuration 3: Si(333) channel cut focused @ 5.9479 keV
if Config==3:
    pos igap 7.621
    pos dcmenergy 5.9466
    pos dcmoffset 16+1.99
    pos hs2ycentre 15.7+1.99
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
    pos hm1y -97.925+1.99
    pos hm1x 0.94
    pos hm1pitch 3.06
    pos hm1yaw 0.4
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1+1.99
    pos hm2x -1.4655
    pos hm2pitch 3.3267

# CCC
    pos cccy -131.2
    pos cccx 0.9

# HM3
    pos hm3y 4.8915
    pos hm3pitch -0.45
    pos hm3x 0.936
    pos hm3mainbender 119500
    pos hm3elipticalbender 1190


# Configuration 4: Si(004) channel cut focused @ 5.9357 keV
if Config==4:
    pos cccx -5
    pos igap 7.606
    pos dcmenergy 5.9343
    ienergy.setOrder(5)
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0521
#    pos dcmroll -0.07
    pos dcmroll -0.0385
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch -0.51
    pos hm1x 2.5  #  1.35  ## changed from 1.2
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
    pos hm3y 4.8915
    pos hm3pitch -0.45
    pos hm3x 0.795
    pos hm3mainbender 119500
    pos hm3elipticalbender 1190

# Configuration 5: Si(044) channel cut focused @ 8.1417 keV
if Config==5:    
    cccx.asynchronousMoveTo(-5)
    igap.asynchronousMoveTo(7.47)
    dcmenergy.asynchronousMoveTo( 8.1385)
    dcmoffset.asynchronousMoveTo( 16)
    hs2ycentre.asynchronousMoveTo( 15.7)
    dcmfpitch.asynchronousMoveTo( 5)
    dcmfroll.asynchronousMoveTo( 5)
    while cccx.isBusy() or igap.isBusy() or dcmenergy.isBusy() or dcmoffset.isBusy() or hs2ycentre.isBusy():
        sleep(0.1)
    dcmroll.moveTo ( -0.06)    
    dcmroll.moveTo ( -0.041)   #( -0.0185)   
    dcmpitch.moveTo( 0.04)
    dcmpitch.moveTo( 0.0517)   # (0.0458)  
    print 'First part done!'
    
    print 'Remove hm1'
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    hm1pitch.asynchronousMoveTo( 0)
    hm1x.asynchronousMoveTo(2.7)
    hd3x.asynchronousMoveTo( -20.975)
    hs1xgap.asynchronousMoveTo( 1.5)
    while hm1pitch.isBusy() or hm1x.isBusy() or hd3x.isBusy() or hs1xgap.isBusy():
        sleep(0.1)    
    print 'Ready for dcmfpitch scan'
    rscan dcmfpitch -3 3 0.1 hd3iamp4
    dcmfpitch.asynchronousMoveTo(peakdata.cfwhm)
    hd3x.asynchronousMoveTo( -1)
    hd4x.asynchronousMoveTo( -23.558)
    hs1xgap.asynchronousMoveTo( 0.1)
    while dcmfpitch.isBusy() or hd3x.isBusy() or hd4x.isBusy() or hs1xgap.isBusy():
        sleep(0.1)    
    print 'Ready for dcmfroll scan'
    rscan dcmfroll -2 2.5 0.05 hd4iamp6
    dcmfroll.asynchronousMoveTo( peakdata.cfwhm)
    hd4x.asynchronousMoveTo( -1)
    hs1xgap.asynchronousMoveTo(1.5)
    dcmoffset.asynchronousMoveTo( 22.3)
    hs2ycentre.asynchronousMoveTo( 22)
    while dcmoffset.isBusy() or hs2ycentre.isBusy() or hd4x.isBusy() or hs1xgap.isBusy():
        sleep(0.1)    
    print 'hs1 moved back, dcmoffset changed'   
# HM1
    print 'start moving hm1'
    hm1y.asynchronousMoveTo( -91.745)
    hm1x.asynchronousMoveTo( 0.475)
    hm1pitch.asynchronousMoveTo( 2.836)
    hm1yaw.asynchronousMoveTo( 0.3)
    hm1roll.asynchronousMoveTo( 0.02)
    while hm1y.isBusy() or hm1x.isBusy() or hm1yaw.isBusy() or hm1roll.isBusy():
        sleep(0.1)    
    print 'hm1 in position' 
# HM2
    print 'start moving hm2'
    hm2y.asynchronousMoveTo( 10.4)
    hm2x.asynchronousMoveTo( -1.6522)
    hm2pitch.asynchronousMoveTo( 3.116)
    while hm2y.isBusy() or hm2pitch.isBusy():
        sleep(0.1)    
    print 'hm2 in position' 
# CCC
    print 'start moving ccc'
    cccy.asynchronousMoveTo( -10.5)
    cccx.asynchronousMoveTo( 4.35)
    while cccy.isBusy() or cccx.isBusy():
        sleep(0.1)    
    print 'ccc in position' 
# HM3
    hm3y.asynchronousMoveTo( 4.8915)
    hm3x.asynchronousMoveTo( 1.4)
    hm3pitch.asynchronousMoveTo( -0.4)
    hm3mainbender.asynchronousMoveTo( 121000)
    hm3elipticalbender.asynchronousMoveTo( 1190)
    while hm3y.isBusy() or hm3x.isBusy():
        sleep(0.1)    
    print 'hm3 in position'
# Configuration 6: 2.5 keV defocused in both directions
if Config==6:
    pos igap 15.415
    pos dcmenergy 2.5
    ienergy.setOrder(1)
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0521
    pos dcmroll -0.07
    pos dcmroll -0.0385
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch -0.41
    pos hm1x 2
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
    pos hm1y -146.87
    pos hm1x 2.674
    pos hm1pitch 6.426
    pos hm1yaw -0.3
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1
    pos hm2x -4.28
    pos hm2pitch 6.6353
    
# CCC
    pos cccx -5

#HM3
    pos hm3y 4.8915
    pos hm3pitch -0.46
    pos hm3x 1.06
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
    pos hm1yaw -0.3
    pos hm1roll 0.0

# HM2
    pos hm2y 4.1
    pos hm2x -4.28
    pos hm2pitch 6.6353
    
# CCC
    pos cccx -5

#HM3
    pos hm3y 4.8915
    pos hm3pitch -0.4
    pos hm3x 1.5636
    pos hm3mainbender 121000
    pos hm3elipticalbender 1190
