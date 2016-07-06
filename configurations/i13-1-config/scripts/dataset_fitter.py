from gda.device.detector import INexusProviderDataSetProcessor

from uk.ac.diamond.scisoft.analysis.dataset.function import Integrate2D

from uk.ac.diamond.scisoft.analysis.fitting.functions import Gaussian, Offset
from uk.ac.diamond.scisoft.analysis.optimize import GeneticAlg
from uk.ac.diamond.scisoft.analysis.fitting import Fitter 

from org.eclipse.january.dataset import DatasetFactory

from gda.analysis import RCPPlotter

import scisoftpy as dnp
import pi

class DataSetFitter(INexusProviderDataSetProcessor):
    
    def getName(self):
        return "datasetFitter"

    def process(self, detectorName, dataName, ds):
        integrator = Integrate2D()
#         dsy = ds.sum(0)
#         dsx = ds.sum(1)
#         dsyaxis = dnp.arange(dsy.shape[0])
#         dsxaxis = dnp.arange(dsy.shape[0])
        dsy, dsx = integrator.value(ds)
        dsyaxis = DatasetFactory.createRange(dsy.shape[0])
        dsxaxis = DatasetFactory.createRange(dsx.shape[0])
        
        gaussian = Gaussian(dsyaxis.min(), dsyaxis.max(), dsyaxis.max()-dsyaxis.min(), (dsyaxis.max()-dsyaxis.min())*(dsy.max()-dsy.min()) )
        gaussian.getParameter(2).setLowerLimit(0)
        if self.maxwidth is not None:
            gaussian.getParameter(1).setUpperLimit(self.maxwidth)
        ansy = Fitter.fit( dsyaxis, dsy, GeneticAlg(.001), [ gaussian, Offset( dsy.min(),dsy.max() ) ] )
        
        gaussian = Gaussian(dsxaxis.min(), dsxaxis.max(), dsxaxis.max()-dsxaxis.min(), (dsxaxis.max()-dsxaxis.min())*(dsx.max()-dsx.min()) )
        gaussian.getParameter(2).setLowerLimit(0)
        if self.maxwidth is not None:
            gaussian.getParameter(1).setUpperLimit(self.maxwidth)
        try:
            ansx = Fitter.fit( dsxaxis, dsx, GeneticAlg(.001), [ gaussian, Offset( dsx.min(),dsx.max() ) ] )
            RCPPlotter.plot("Data Vector", dsxaxis,ansx.display(dsxaxis)[0]);
        except java.lang.IllegalArgumentException:
            # Probably cannot find Plot_Manager on the finder
            ansx = Fitter.fit( dsxaxis, dsx, GeneticAlg(.001), [ gaussian, Offset( dsx.min(),dsx.max() ) ] )
        #dsyaxis = dsyaxis.subSampleMean(dsy.dimensions[0]/2)
        #dsy = dsy.subSampleMean(dsy.dimensions[0]/2)
        #dsxaxis = dsxaxis.subSampleMean(dsx.dimensions[0]/2)
        #dsx = dsx.subSampleMean(dsx.dimensions[0]/2)        
        
        peaky = ansy[0].getValue()
        fwhmy = ansy[1].getValue()
        areay = ansy[2].getValue()
        offsety = ansy[3].getValue() / dsx.shape[0]
        
        peakx = ansx[0].getValue()
        fwhmx = ansx[1].getValue()
        areax = ansx[2].getValue()
        offsetx = ansx[3].getValue() / dsy.shape[0]
        
        background = (offsetx+offsety)/2.
        fwhmarea = fwhmy*fwhmx*pi/4
        topy = areay / fwhmarea
        topx = areax / fwhmarea
        
        if xoffset==None:
            xoffset=0
        
        if yoffset==None:
            yoffset=0
        
        return background, peakx+xoffset, peaky+yoffset, topx, topy, fwhmx, fwhmy, fwhmarea
        
        
        return None

    def getExtraNames(self):
        return "peak"
    
    def getOutputFormat(self):
        return "%5.5g"