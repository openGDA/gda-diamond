import scisoftpy as dnp
from gda.data import PathConstructor

def restorerois(scan,detector):
    if type(scan) == int:
        f = dnp.io.load(PathConstructor.createFromDefaultProperty()+"/"+ str(scan) + ".dat")
    else:
        f = dnp.io.load(scan)
    roi = 0
    while True:
        roi += 1
        if 'roi' + str(roi) + '_X' in f.keys():

            detector.addRoi(f[f.keys().index('roi' + str(roi) + '_X')][0],
                            f[f.keys().index('roi' + str(roi) + '_Y')][0],
                            f[f.keys().index('roi' + str(roi) + '_Width')][0],
                            f[f.keys().index('roi' + str(roi) + '_Height')][0],
                            f[f.keys().index('roi' + str(roi) + '_Angle')][0],
                            )
        else:
            break
    
    print str(roi-1) + " ROIs added"
