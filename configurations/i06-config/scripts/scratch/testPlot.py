
# sfield is a 3D dataset
# xaxis, yaxis, zaxis are 1D datasets
#http://trac.diamond.ac.uk/scientific_software/wiki/SciRCPPlotServer


from uk.ac.diamond.scisoft.analysis.plotserver import *
from uk.ac.diamond.scisoft.analysis.plotserver import GuiPlotMode;


from gda.analysis.io import JPEGLoader, TIFFImageLoader, ConvertedTIFFImageLoader
from org.eclipse.dawnsci.analysis.api.io import ScanFileHolderException

from gda.analysis import ScanFileHolder
from gda.analysis.functions.dataset import MakeMask;
from gda.analysis import DataSet;

# scan testMotor1 -2*math.pi 2*math.pi 0.1 PlotXY("testMotor1",["math.sin(testMotor1)+random.random()"]), dummyCounter 0.1

data = ScanFileHolder()

data.loadSRS("/home/cop98/Dev/gdaDev/gda-config/i07/users/data/operation/6.dat")

xaxis=data.getAxis("testMotor1")
yaxis=data.getAxis("y1")
zaxis=data.getAxis(2)

plotData = DataBean()                         # create new data bean
plotData.addAxis(AxisMapBean.XAXIS, xaxis)    # stuff axis 2D datasets
# plotData.addAxis(AxisMapBean.YAXIS, yaxis)

amb = AxisMapBean(AxisMapBean.FULL)           # create new FULL axis mapping bean
#amb.setAxisID([AxisMapBean.XAXIS, AxisMapBean.YAXIS])
amb.setAxisID([AxisMapBean.XAXIS])

# list the axis datasets' names
scalar = DataSetWithAxisInformation()         # create data and axis-mapping container
scalar.setAxisMap(amb)                        # set axis-mapping (NB need to set this before setting data)
scalar.setData(yaxis)                         # set data

plotData.addData(scalar)                      # add dataset
guiBean = GuiBean()                           # create a GUI bean
guiBean[GuiParameters.PLOTMODE] = GuiPlotMode.ONED

# specify the plotting mode
ps = finder.find("plot_server")               # find plot server
ps.updateGui("Plot View", guiBean)            # send the GUI bean to the client
ps.setData("Plot View", plotData)             # fire plot data to it

