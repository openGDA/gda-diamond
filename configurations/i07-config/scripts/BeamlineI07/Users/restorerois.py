import scisoftpy as dnp
from gda.jython import InterfaceProvider

def restorerois(scan):
    if type(scan) == int:
        f = dnp.io.load(InterfaceProvider.getPathConstructor().createFromDefaultProperty()+"/"+ str(scan) + ".dat")
    else:
        f = dnp.io.load(scan)
    roi = 0
    bean = dnp.plot.getbean(name="Area Detector")
    oldrois = dnp.plot.getrois(bean)
    newrois = dnp.plot.roi_list()
    while True:
        r = dnp.plot.roi.rectangle()
        if 'roi' + str(roi+1) + '_X' in f.keys():
            roi += 1
            r.setName('Region ' + str(roi))
            r.setPoint((f[f.keys().index('roi' + str(roi) + '_X')][0], f[f.keys().index('roi' + str(roi) + '_Y')][0]))
            r.setLengths((f[f.keys().index('roi' + str(roi) + '_Width')][0], f[f.keys().index('roi' + str(roi) + '_Height')][0]))
            r.setAngle(f[f.keys().index('roi' + str(roi) + '_Angle')][0])
            newrois.append(r)
        else:
            break
    if roi > 0:
        # doesn't work unless we set a single ROI first; coords unimportant as this is overwritten anyway
        roi1 = dnp.jython.jyroi.rectangle()
        roi1.setName("Region 1")
        dnp.plot.setroi(bean, roi1)

        dnp.plot.setrois(bean, newrois)
        dnp.plot.setbean(bean, name="Area Detector")
    print str(roi) + " ROIs added"