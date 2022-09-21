'''
function and dictionary to define sample positions and carbon tape positions during single GDA server session.

Created on Sep 20, 2022

@author: fy65
'''
from gdaserver import x,y,z,th,phi,chi  # @UnresolvedImport
from gda.jython.commands.GeneralCommands import alias

sample_pos = {"x":0, "y":0, "z":0, "th":0, "phi":0, "chi":0}
carbon_tape_pos = {"x":0, "y":0, "z":0, "th":0, "phi":0, "chi":0}

def save_sample_positions():
    global sample_pos
    sample_pos["x"] = float(x.getPosition())
    sample_pos["y"] = float(y.getPosition())
    sample_pos["z"] = float(z.getPosition())
    sample_pos["th"] = float(th.getPosition())
    sample_pos["phi"] = float(phi.getPosition())
    sample_pos["chi"] = float(chi.getPosition())
    print("sample positions are saved.")
    
alias("save_sample_positions")

def save_carbon_tape_positions():
    global carbon_tape_pos
    carbon_tape_pos["x"] = float(x.getPosition())
    carbon_tape_pos["y"] = float(y.getPosition())
    carbon_tape_pos["z"] = float(z.getPosition())
    carbon_tape_pos["th"] = float(th.getPosition())
    carbon_tape_pos["phi"] = float(phi.getPosition())
    carbon_tape_pos["chi"] = float(chi.getPosition())
    print("carbon tape positions are saved.")

alias("save_carbon_tape_positions")
    
def move_to_sample_positions():
    global sample_pos
    x.asynchronousMoveTo(sample_pos["x"])
    y.asynchronousMoveTo(sample_pos["y"])
    z.asynchronousMoveTo(sample_pos["z"])
    th.asynchronousMoveTo(sample_pos["th"])
    phi.asynchronousMoveTo(sample_pos["phi"])
    chi.asynchronousMoveTo(sample_pos["chi"])
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    print("move to sample positions completed.")
    
alias("move_to_sample_positions")

def move_to_carbon_tape_positions():
    global carbon_tape_pos
    x.asynchronousMoveTo(carbon_tape_pos["x"])
    y.asynchronousMoveTo(carbon_tape_pos["y"])
    z.asynchronousMoveTo(carbon_tape_pos["z"])
    th.asynchronousMoveTo(carbon_tape_pos["th"])
    phi.asynchronousMoveTo(carbon_tape_pos["phi"])
    chi.asynchronousMoveTo(carbon_tape_pos["chi"])
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    th.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    print("move to carbon tape positions completed.")
    
alias("move_to_carbon_tape_positions")

    