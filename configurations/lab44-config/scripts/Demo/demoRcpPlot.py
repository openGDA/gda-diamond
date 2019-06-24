from gda.analysis import RCPPlotter

from uk.ac.diamond.scisoft.analysis.plotserver import GuiBean;
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters;
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList;
from org.eclipse.january.dataset import DatasetFactory

pp=RCPPlotter()
pp.plot("Area Detector", DatasetFactory.createFromObject(range(100)))



#This is used to plot on the PlotView
#d = DataSet.arange(10000)
#d.shape = [100,100]

d=DatasetFactory.createRange(10000)
d.shape = [100,100]
# or, d = DataSet.arange(10000).reshape((100,100)) in GDA v8.12

pp.imagePlot("Area Detector", d)


#This is used to plot on the ImageExploreView
pp.plotImageToGrid("Image Explorer", DatasetFactory.ones([20,30]) )
pp.plotImageToGrid("Image Explorer", "/home/xr56/temp/p100kImage26455.tif")

#RCPPlotter().plotImageToGrid("Image Explorer","/home/xr56/temp/pilatus100K/p686905.tif")
RCPPlotter().scanForImages("Image Explorer", "/dls/i06/data/2010/cm1895-1/demoImages")


#ROI
#Get ROI info

gbean = pp.getGuiBean("Area Detector")

gbean

#{ROIData=Start (36.0000, 27.0000) Size (11.0000,10.0000) Angle 0.00000, PlotMode=2D, PlotID=09421fb4-720f-4847-a40e-e8cafeacba84}
gKeys = gbean.keySet() #[ROIData, PlotMode, PlotID]
gValues = gbean.values() # [Start (36.0000, 27.0000) Size (11.0000,10.0000) Angle 0.00000, 2D, 09421fb4-720f-4847-a40e-e8cafeacba84]


roidata=gbean.get("ROIData")
roidata=gbean["ROIData"];
type(roidata) 
#<type 'uk.ac.diamond.scisoft.analysis.dataset.roi.RectangularROI'>
roidata.getPoint()   #array('d', [36.0, 27.0])
roidata.getEndPoint()#array('d', [47.0, 37.0])
roidata.getLengths() #array('d', [11.0, 10.0])
roidata.getAngle()   #0.0

#Set ROI
gpea=GuiBean();
newroi = RectangularROI(22,33,44,55,0);
gpea.put("ROIData", newroi);
#gpea["ROIData"] = newroi
pp.setGuiBean("Area Detector", gpea);


#For multiple ROIs:

gbean2 = pp.getGuiBean("Area Detector")
lb = gbean2.get("ROIDataList") # [Start (22.0000, 33.0000) Size (44.0000,55.0000) Angle 0.00000, Start (32.0000, 47.0000) Size (50.0000,17.0000) Angle 0.00000]
lb = gbean2["ROIDataList"]     #[Start (22.0000, 33.0000) Size (44.0000,55.0000) Angle 0.00000, Start (32.0000, 47.0000) Size (50.0000,17.0000) Angle 0.00000]

len(gbean2) #4

roi1 = gbean2["ROIDataList"][0] #Start (22.0000, 33.0000) Size (44.0000,55.0000) Angle 0.00000
ro12 = gbean2["ROIDataList"][1] #Start (32.0000, 47.0000) Size (50.0000,17.0000) Angle 0.00000



