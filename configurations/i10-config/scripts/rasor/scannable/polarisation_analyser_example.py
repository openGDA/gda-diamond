'''
Created on 10 Apr 2018

@author: fy65
'''
from gdaserver import pgm_energy, thp, ttp, py, pz
from utils.ExceptionLogs import localStation_exception
from gda.jython.commands.GeneralCommands import alias
import sys

print "-"*100
print "Creating Multilayer Analyser example objects:"
print " 1. 'ml'  - define multilayer object using (name, d_spacing (A), start_energy(eV), stop_energy(eV), thp_offset(deg), pos_z(mm), pos_y(mm))"
print " 2. 'mss' - define multilayer selector scannable using (name, multilayer_list, pz_scannable, py_scannable)"
print " 3. 'pa'  - define polarisation analyser scannable using (name, thp_scannable, ttp_scannable, multilayer_selector_scannable, energy_scannable)"
try:
    from rasor.scannable.polarisationAnalyser import Multilayer, MultilayerSelectorScannable, PolarisationAnalyser
    # name, d_spacing (A), start_energy(eV), stop_energy(eV), thp_offset(deg), pos_z(mm), pos_y(mm)
    ml = [
        Multilayer("mn", 13.7, 600, 700, 1.17, -14.5, 1.5),
        Multilayer("o",  16.2, 510, 550, 0,      0,   1.5)]
    # name, multilayer_list, pz_scannable, py_scannable
    mss = MultilayerSelectorScannable("mss", ml, pz, py)
    # name, thp_scannable, ttp_scannable, multilayer_selector_scannable, energy_scannable
    pa = PolarisationAnalyser("pa", thp, ttp, mss, pgm_energy)
    print "Usage: pos mss            to find out which MSS you are on"
    print "Usage: pos mss <num>      to select MSS by number"
    print "Usage: pos mss 'string'   to select MSS by name"
    print "Usage: pos pa             to find out which PA you are on"
    print "Usage: pos pa <num>       to set pa for a given energy in eV"
    print "Usage: pos pa 0           to set pa for a the energy in configured energy scannable"
    alias("pa")
except:
    localStation_exception(sys.exc_info(), "initialising polarisation analyser")