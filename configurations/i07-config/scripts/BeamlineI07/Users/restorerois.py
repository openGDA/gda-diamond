import scisoftpy as dnp

def list_rois(view):
    list_of_rois = dnp.plot.getrois(name=view)
    if list_of_rois is None or list_of_rois.__len__() == 0 :
        print("No ROIs defined")
        return
    for old_roi in list_of_rois :
        print(str(old_roi))

def add_roi(name, xpos, ypos, width, height, view):
    list_of_rois = dnp.plot.getrois(name=view)
    r = dnp.plot.roi.rectangle()
    r.setName(name)
    r.setPoint((xpos, ypos))
    r.setLengths((width, height))
    r.setPlot(True)
    list_of_rois.append(r)
    dnp.plot.setrois(list_of_rois, name=view)
