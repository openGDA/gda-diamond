from gda.data import NumTracker
from gda.data import PathConstructor
import scisoftpy as dnp
i22NumTracker = NumTracker("i22");

file = open(PathConstructor.createFromDefaultProperty()+"pitch_parameters_linearBragg.csv","a")
file.write("File, Energy, Bragg, 1/cos(Bragg), finepitch_peak, finepitch_max, intensity, pitch_peak\n")
file.close()

for x in dnp.linspace(29.63,5.6746,40,True):
    energyPos = 12.3985/(6.2695*dnp.sin(dnp.radians(x)))
    print energyPos
    pos energy energyPos
    braggAngle = dcm_bragg.getPosition()
    braggInRad = dnp.radians(braggAngle)
    oneOverCosBragg = 1 / dnp.cos(braggInRad)
    pos dcm_finepitch 0
    pos dcm_pitch 0
    sleep(1800)
    setTitle("Pitch scan for "+energyPos.__str__()+"keV")
    scan dcm_finepitch -150 150 1 topup d4d1	
    positionPeak = peak.result.pos
    positionMax = maxval.result.maxpos
    valueMax = maxval.result.maxval
    pos dcm_finepitch -150
    go peak
    sleep(2)
    pitchval = dcm_pitch.getPosition()
    
    # save the data back out
    fileNumber = int(i22NumTracker.getCurrentFileNumber())
    file = open(PathConstructor.createFromDefaultProperty()+"pitch_parameters_linearBragg.csv","a")
    file.write("%d , %.4f, %.4f, %.5f, %.5f, %.4f, %.4f, %.4f\n" % (fileNumber, energyPos, braggAngle, oneOverCosBragg,positionPeak, positionMax, valueMax, pitchval))
    file.close()
