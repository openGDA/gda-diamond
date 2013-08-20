

# How to start the beamline simulation on dasc-epics.diamond.ac.uk

# To use the EDM
launcher --port=6064 &

# For i06 EDM
/dls_sw/work/R3.14.8.2/ioc/BL06I/BL/bin/linux-x86/stBL06I-gui &

# From terminal, set the server port before using caget/caput
export EPICS_CA_SERVER_PORT=6064



####################
How to restart the IOCs

ssh dasc-epics
sudo /sbin/service epics-soft-iocs restart <ioc name>

where <ioc name> is one of the following:

BL-machine-sim  - simulates the ID motors for ALL beamlines
BL06I-CS-SIM-01 - runs the beamline interface to the I06 ID motors
BL06I-MO-SIM-02 - simulates the PGM motors and runs the energy control and fast scan software

So if the ID appears to be not working, you might need to restart BL06I-CS-SIM-01 and/or BL-machine-sim.
If the PGM is not working or the fast scan is somehow stuck, you will need to restart BL06I-MO-SIM-02.

If you restart BL-machine-sim, beamline control of the ID is disabled by default so you need to type the following afterwards:

export EPICS_CA_SERVER_PORT=6064
caput SR06I-MO-SERVC-01:IDBLENA 0


If you restart BL06I-MO-SIM-02, the ID energy coefficients need to be restored.  I've created a script to do this:

export EPICS_CA_SERVER_PORT=6064
/home/els59/I06/energySimulation/caputCoeffs.sh

