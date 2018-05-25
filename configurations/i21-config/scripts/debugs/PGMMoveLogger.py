'''
Created on 2 Mar 2018

@author: fy65
'''
import time
from gdaserver import pgmEnergy

def moveEnergy(new_pos, resolution=0.01, logfile="/dls_sw/i21/logs/PGMEnergyMove.log"):
    energy.moveTo(new_pos)  # @UndefinedVariable
    cur_val = float(pgmEnergy.getPosition())
    if (abs(cur_val-new_pos)>(0.5*resolution)):
        with open(logfile, 'a') as outfile:
            message='{} : energy move failed. PGM current value = {}, demand value = {}\n'.format(time.asctime(), str(cur_val), str(new_pos))
            outfile.write(message)
            
def movePGMEnergy(new_pos, resolution=0.01, logfile="/dls_sw/i21/logs/PGMEnergyMove.log"):
    pgmEnergy.moveTo(new_pos)  # @UndefinedVariable
    cur_val = float(pgmEnergy.getPosition())
    if (abs(cur_val-new_pos)>(0.5*resolution)):
        with open(logfile, 'a') as outfile:
            message='{} : pgmEnergy move failed. PGM current value = {}, demand value = {}\n'.format(time.asctime(), str(cur_val), str(new_pos))
            outfile.write(message)
