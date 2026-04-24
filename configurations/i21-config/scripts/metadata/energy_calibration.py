'''
Created on 20 Apr 2026

@author: fy65
'''
from gdascripts.scannable.virtual_scannable import VirtualScannable

energy_dispersion = VirtualScannable("energy_dispersion", initial_value=0.0, value_format="%.6f")
elastic_slope = VirtualScannable("elastic_slope", initial_value=0.0, value_format="%.6f")
elastic_offset = VirtualScannable("elastic_offset", initial_value=0.0, value_format="%.3f")