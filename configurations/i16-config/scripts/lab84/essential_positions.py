# All of these postions are based on persistent values which are required
# during localStation but which aren't created automatically. We position
# them manually once, which creates them in the persostence system, so
# that on subsequent restarts, the are created automatically.

# This  script needs to be run after every new deployent, before it can be
# used in either dummy or lab84 mode.

pos delta_axis_offset 0
pos cry_offset 5
pos dcmharmonic 1
pos ref_offset 2
pos bragg_offset 0.271790060076
pos idgap_offset 0.533034663313
pos uharmonic 3
pos delta_offset 0
pos eta_offset -0.7