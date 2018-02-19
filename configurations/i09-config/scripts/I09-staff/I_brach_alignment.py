Config=6

# Configuration 1: 2.5 keV focused
if Config==1:
    pos igap 15.415
    pos dcmenergy 2.5
    ienergy.setOrder(1)
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.03
    pos dcmpitch 0.0517
    pos dcmroll -0.06
    pos dcmroll -0.041
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
    ienergy.setOrder(5)
    pos dcmenergy 5.9466
    pos dcmoffset 16+1.99
    pos hs2ycentre 15.7+1.99
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.03
    pos dcmpitch 0.0517
    pos dcmroll -0.06
    pos dcmroll -0.041
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch -0.51
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
    pos cccx -5
    pos igap 7.46
    pos dcmenergy 8.1391
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.0510
    pos dcmroll -0.0430
    hd3iamp4.setGain("10^4 low noise")
    hd4iamp6.setGain("10^4 low noise")
    pos hm1pitch 0
    pos hm1x 2.5
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

    pos dcmoffset 21.75
    pos hs2ycentre 21.5
# HM1
    pos hm1y -92.3
    pos hm1x 0.475
    pos hm1pitch 2.836
    pos hm1yaw 0.3
    pos hm1roll 0.02

# HM2
    pos hm2y 9.85
    pos hm2x -1.6522
    pos hm2pitch 3.116

# CCC
    pos cccy -10.5
    pos cccx 4.51

# HM3
    pos hm3y 4.8915
    pos hm3x 0.940
    pos hm3pitch -0.4
    pos hm3mainbender 121000
    pos hm3elipticalbender 1190

# Configuration 6: 2.5 keV defocused in both directions
if Config==6:
    pos igap 15.415
    pos dcmenergy 2.5
    ienergy.setOrder(1)
    pos dcmoffset 16
    pos hs2ycentre 15.7
    pos dcmfpitch 5
    pos dcmfroll 5
    pos dcmpitch 0.03
    pos dcmpitch 0.0517
    pos dcmroll -0.06
    pos dcmroll -0.041
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
# switch from j to k branch    
if Config==8:  
    try:
        pgmenergy.asynchronousMoveTo(600)
        jgap.asynchronousMoveTo(36.9)   
        ss7xgap.asynchronousMoveTo(0.25)
        ss7ygap.asynchronousMoveTo(0.25)
        photon_move = 1
    except:
        print "********** warning ****************"
        print "photon energy / undulator gap cannot be moved"
        photon_move = 0            
    pos sm3y 21.640
    pos sm3pitch -27754.2
    pos sm3yaw 0.2693
    pos sm3x -1.6484
    pos sm3z 0
    pos sm3roll 0
    if photon_move == 1:
        try:
            sm6iamp27=DisplayEpicsPVClass("sm6iamp27","BL09K-MO-SM-06:IAMP27:I","V","%.5e")
        except:
            print "sm6iamp27 already exists"
        rscan sm3fpitch 3 7 0.01 sm6iamp27
        pos sm3fpitch peakdata.cfwhm
        pos sm3fpitch 5.4
        ss7xgap.asynchronousMoveTo(3)
        pos ss7ygap 0.02
        print "********** Beam is now in the k branch (sm3fpitch optimised) ***************"
    else:
        pos sm3fpitch 5.4
        print "********** Beam is now in the k branch (sm3fpitch NOT optimised) ***************"


# switch from k branch to j branch  
if Config == 9:
    try:
        jenergy.asynchronousMoveTo(0.6)
        photon_move = 1
        ss4xgap.asynchronousMoveTo(0.25)
        ss4ygap.asynchronousMoveTo(0.25)
    except:
        print "********** warning ****************"
        print "photon energy / undulator gap cannot be moved"
        photon_move = 0    
    pos sm3y -19.438
    pos sm3pitch -26773.8
    pos sm3yaw 1750.2
    pos sm3x -1.6220
    pos sm3z 0
    pos sm3roll 0.14740
    if photon_move == 1:
        rscan sm3fpitch 3 7 0.01 sm5amp8 0.1
        pos sm3fpitch peakdata.cfwhm
        ss4xgap.asynchronousMoveTo(3)
        pos ss4ygap 0.02
        print "****** Beam is now in J branch (sm3fpitch optimised) ***************"
    else:
        pos sm3fpitch 5.4
        print "****** Beam is now in J branch (sm3fpitch NOT optimised) ***************"                    