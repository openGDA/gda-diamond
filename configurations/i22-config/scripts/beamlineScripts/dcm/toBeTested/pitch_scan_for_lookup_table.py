from gda.data import NumTracker
from gda.data import PathConstructor
import scisoftpy as dnp
i22NumTracker = NumTracker("i22");

file = open(PathConstructor.createFromDefaultProperty()+"pitch_parameters_linearEnergy.csv","a")
file.write("File, Energy, Bragg, 1/cos(Bragg), finepitch_peak, finepitch_max, intensity, pitch_peak\n")
file.close()

for x in dnp.linspace(4, 20,40,True):
    #energyPos = (12.3985/6.2695)/dnp.sin(dnp.arccos((1/x)))
    #print energyPos
    pos energy x
    braggAngle = dcm_bragg.getPosition()
    braggInRad = dnp.radians(braggAngle)
    oneOverCosBragg = 1 / dnp.cos(braggInRad)
    pos dcm_finepitch 0
    pos dcm_pitch 0
    sleep(2)
    setTitle("Pitch scan for "+x.__str__()+"keV")
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
    file = open(PathConstructor.createFromDefaultProperty()+"pitch_parameters_linearEnergy.csv","a")
    file.write("%d , %.4f, %.4f, %.5f, %.5f, %.4f, %.4f, %.4f\n" % (fileNumber, x, braggAngle, oneOverCosBragg,positionPeak, positionMax, valueMax, pitchval))
    file.close()
