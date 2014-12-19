
from gda.device.scannable import TwoDScanPlotter

class Plotter:
     
    def __init__(self, name, Z_colName, plotViewName):
        self.xstart = 0
        self.xstep = 1
        self.ystart = 0
        self.ystep = 1
        self.plotter = self.createPlotter(name, Z_colName, plotViewName)

    def createPlotter(self,name,Z_colName,plotViewName):
        plotter = TwoDScanPlotter()
        plotter.setName(name)
        plotter.setZ_colName(Z_colName)
        plotter.setPlotViewname(plotViewName)
        return plotter

    def getPlotter(self):
        return self.plotter
    
    def setAxis(self,xstop, ystop):
        self.plotter.setXArgs(self.xstart, xstop, self.xstep)
        self.plotter.setYArgs(self.ystart, ystop, self.ystep)