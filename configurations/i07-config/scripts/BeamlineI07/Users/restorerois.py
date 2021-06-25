import scisoftpy as dnp
from gda.jython import InterfaceProvider

VIEW_NAME = "Area Detector"

def restorerois(scan):
    if type(scan) == int:
        f = dnp.io.load(InterfaceProvider.getPathConstructor().createFromDefaultProperty()+"/"+ str(scan) + ".dat")
    else:
        f = dnp.io.load(scan)
    roi = 0
    oldrois = dnp.plot.getrois(name=VIEW_NAME)
    newrois = dnp.plot.roi_list()
    prefix = 'roi'
    if 'Region_1_X' in f.keys():
        prefix = 'Region_'
    while True:
        r = dnp.plot.roi.rectangle()
        if prefix + str(roi+1) + '_X' in f.keys():
            roi += 1
            r.setName('Region ' + str(roi))
            r.setPoint((float(f[f.keys().index(prefix + str(roi) + '_X')][0]), float(f[f.keys().index(prefix + str(roi) + '_Y')][0])))
            r.setLengths((float(f[f.keys().index(prefix + str(roi) + '_Width')][0]), float(f[f.keys().index(prefix + str(roi) + '_Height')][0])))
            r.setAngle(float(f[f.keys().index(prefix + str(roi) + '_Angle')][0]))
            r.setPlot(True)
            newrois.append(r)
        else:
            break
    if roi > 0:
        dnp.plot.setrois(newrois, name=VIEW_NAME)
    print("{} ROIs added".format(roi))
