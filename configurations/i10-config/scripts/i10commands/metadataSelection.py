'''
Created on Aug 25, 2021

@author: fy65
'''
from gdascripts.metadata.nexus_metadata_commands import enable_meta,\
    disable_meta
from gda.configuration.properties import LocalProperties

scattering_metadata = ['s4', 's5', 's6', 'm4', 'rasor', 'lakeshore340']
absorption_metadata = ['s7','s8', 's9', 'm6', 'mes', 'lakeshore336', 'em']

active_profiles = LocalProperties.getStringArray("gda.spring.profiles.active")

if "scattering" in active_profiles and "absorption" in active_profiles:
    scattering_enabled = True
    absorption_enabled = True
    
    def scattering():
        global absorption_enabled, scattering_enabled
        if absorption_enabled:
            disable_meta(*absorption_metadata)
            absorption_enabled = False
        if not scattering_enabled:
            enable_meta(*scattering_metadata)
            scattering_enabled = True
    
    def absorption():
        global absorption_enabled, scattering_enabled
        if scattering_enabled:
            disable_meta(*scattering_metadata)
            scattering_enabled = False
        if not absorption_enabled:
            enable_meta(*absorption_metadata)
            absorption_enabled = True
    
    def both():
        global absorption_enabled, scattering_enabled
        if not scattering_enabled:
            enable_meta(*scattering_metadata)
            scattering_enabled = True
        if not absorption_enabled:
            enable_meta(*absorption_metadata)
            absorption_enabled = True
    
