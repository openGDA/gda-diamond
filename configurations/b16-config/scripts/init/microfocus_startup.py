#run "init/microfocus_startup.py"

from gda.configuration.properties import LocalProperties
import os.path
print "setting up scripts which run behind the microfocus and experiment perspectives"

uk_ac_gda_beamline_b16 = os.path.join(LocalProperties.get("gda.install.git.loc"), 'gda-diamond.git', 'plugins', 'uk.ac.gda.beamline.b16')
execfile(os.path.join(uk_ac_gda_beamline_b16, 'scripts', 'microfocus', 'map.py'))
execfile(os.path.join(uk_ac_gda_beamline_b16, 'scripts', 'microfocus', 'microfocus_elements.py'))

alias("mapscan") #@UndefinedVariable

#b16beansfactory = BeansFactory()
#print "Configuring beans factory"
#b16beansfactory.setClassList(["uk.ac.gda.beans.exafs.DetectorParameters", "uk.ac.gda.beans.vortex.VortexParameters", "uk.ac.gda.beans.microfocus.MicroFocusScanParameters"])



from uk.ac.gda.beans.vortex import VortexParameters
from uk.ac.gda.util.beans.xml import XMLHelpers
import java.io.File

def vortex(vortexParameters):
    # write to template
    XMLHelpers.writeToXML(VortexParameters.mappingURL, vortexParameters, java.io.File(xmap.getConfigFileName())); #@UndefinedVariable
    # tell xmap to load from the template
    xmap.loadConfigurationFromFile() #@UndefinedVariable

#when(mca0.getRegionsOfInterestCount()).thenReturn(
#        toNative([[100., 80.], [200., 180.], [300., 280.]]))
#
#when(mca1.getRegionsOfInterestCount()).thenReturn(
#        toNative([[101., 81.], [201., 181.], [301., 281.]]))
#when(mca0.getNumberOfChannels()).thenReturn(java.lang.Long(5));
#when(mca1.getNumberOfChannels()).thenReturn(java.lang.Long(5));
#        
#when(mca0.getData()).thenReturn(jarray.array([1,2,3,4,5], 'd'));
#when(mca1.getData()).thenReturn(jarray.array([11,12,13,14,15], 'd'));
         
                
                
