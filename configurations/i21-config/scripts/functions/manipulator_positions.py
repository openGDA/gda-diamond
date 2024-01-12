'''
function and dictionary to define sample positions and carbon tape positions during single GDA server session.

Created on Sep 20, 2022

@author: fy65
'''
from gdaserver import x,y,z,th,phi,chi  # @UnresolvedImport
from gda.jython.commands.GeneralCommands import alias

# define dictionary to store positions
sample_pos = {"sample": {"x":0, "y":0, "z":0, "phi":0, "chi":0}}
carbon_tape_pos = {"carbon": {"x":0, "y":0, "z":0, "phi":0, "chi":0}}

def save_sample_positions(name = "sample"):
    global sample_pos
    sample_pos[name]["x"] = float(x.getPosition())
    sample_pos[name]["y"] = float(y.getPosition())
    sample_pos[name]["z"] = float(z.getPosition())
    sample_pos[name]["phi"] = float(phi.getPosition())
    sample_pos[name]["chi"] = float(chi.getPosition())
    print("sample positions are saved with key %s." % name)
    
alias("save_sample_positions")

def save_carbon_tape_positions(name = "carbon"):
    global carbon_tape_pos
    carbon_tape_pos[name]["x"] = float(x.getPosition())
    carbon_tape_pos[name]["y"] = float(y.getPosition())
    carbon_tape_pos[name]["z"] = float(z.getPosition())
    carbon_tape_pos[name]["phi"] = float(phi.getPosition())
    carbon_tape_pos[name]["chi"] = float(chi.getPosition())
    print("carbon tape positions are saved.")

alias("save_carbon_tape_positions")
    
def move_to_sample_positions(name = "sample"):
    global sample_pos
    x.asynchronousMoveTo(sample_pos[name]["x"])
    y.asynchronousMoveTo(sample_pos[name]["y"])
    z.asynchronousMoveTo(sample_pos[name]["z"])
    phi.asynchronousMoveTo(sample_pos[name]["phi"])
    chi.asynchronousMoveTo(sample_pos[name]["chi"])
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    print("move to sample positions to '%s' completed." % name)
    
alias("move_to_sample_positions")

def move_to_carbon_tape_positions(name = "carbon"):
    global carbon_tape_pos
    x.asynchronousMoveTo(carbon_tape_pos[name]["x"])
    y.asynchronousMoveTo(carbon_tape_pos[name]["y"])
    z.asynchronousMoveTo(carbon_tape_pos[name]["z"])
    phi.asynchronousMoveTo(carbon_tape_pos[name]["phi"])
    chi.asynchronousMoveTo(carbon_tape_pos[name]["chi"])
    x.waitWhileBusy()
    y.waitWhileBusy()
    z.waitWhileBusy()
    phi.waitWhileBusy()
    chi.waitWhileBusy()
    print("move to carbon tape positions '%s' completed." % name)
    
alias("move_to_carbon_tape_positions")

    