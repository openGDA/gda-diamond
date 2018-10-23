'''
Script to run after the polarimeter is properly installed on beamline and EPICS IOC for it up and running.

Created on 9 Mar 2017

@author: fy65
'''


from __main__ import beanAdder  # @UnresolvedImport
from gda.configuration.properties import LocalProperties
import sys

gda_git_loc=LocalProperties.get(LocalProperties.GDA_GIT_LOC);
# files for new bean definitions
#properties_definition_file=str(gda_git_loc)+"/gda-diamond.git/configurations/i06-shared/properties/_common/gdaProperties.xml"
device_bean_definition_file=str(gda_git_loc)+"/gda-diamond.git/configurations/optics-config/servers/main/live/devices/polarimeter.xml"
scannable_bean_definition_file=str(gda_git_loc)+"/gda-diamond.git/configurations/optics-config/servers/main/_common/scannables/polarimeter.xml"

#add polarimeter beans to GDA server
beanAdder.loadAdditionalBeans([device_bean_definition_file, scannable_bean_definition_file])

print "Create and add 'Polarimeter' objects:"
print Polarimeter  # @UndefinedVariable

#section to programmably inject referenced objects from parent context
sys.path.append(str(gda_git_loc)+"/gda-diamond.git/configurations/optics-config/scripts")
#import polarimeter scannable objects
from polarimeter.polarimeterHexapod import hpx, hpy, hpz, hpa, hpb, hpc, hexapod  # @UnusedImport
from polarimeter.polarimeterTemperatureMonitor import anatemp,rettemp  # @UnusedImport
from polarimeter.Scaler8512 import ca01sr,ca02sr,ca03sr,ca04sr,ca05sr,ca06sr,ca07sr,ca08sr,scaler  # @UnusedImport