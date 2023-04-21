'''
copy live I16 beamline GDA var cache data to dummy var on each new deployment of GDA release.

Please note these cache data are only copied once if they are not present at dummy GDA server startup time.
 
Created on Apr 5, 2023

@author: fy65
'''
from org.slf4j import LoggerFactory

logger = LoggerFactory.getLogger(__name__)
# install UB matrix data files in dummy mode when first time run GDA server after checkout GDA source codes from repositories!
from gda.configuration.properties import LocalProperties
import os
from distutils.dir_util import copy_tree
from shutil import copyfile

def install_cache_data():
    cache_directory_to_copy = ["diffcalc", "oldStyleShelveIO", "nff"]
    
    for each in cache_directory_to_copy:
        to_directory = os.path.join(LocalProperties.get(LocalProperties.GDA_VAR_DIR), str(each))    
        if not os.path.exists(to_directory):
            #install UB data
            from_directory = os.path.join("/dls_sw/i16/software/gda_versions/var", str(each))
            logger.info("Install {} directory and its contents in {}", each, to_directory)
            copy_tree(from_directory, to_directory)
            
    cache_file_to_copy = ["reffilename.log"]
    
    for each in cache_file_to_copy:
        to_file = os.path.join(LocalProperties.get(LocalProperties.GDA_VAR_DIR), str(each))    
        if not os.path.exists(to_file):
            #install UB data
            from_file = os.path.join("/dls_sw/i16/software/gda_versions/var", str(each))
            logger.info("Install {} file in directory {}", each, to_file)
            copyfile(from_file, to_file)
