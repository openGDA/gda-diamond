# All of these postions are based on persistent values which are required
# during localStation but which aren't created automatically. We position
# them manually once, which creates them in the persistence system, so
# that on subsequent restarts, the are created automatically.

# This  script needs to be run after every new deployment, before it can be
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

# These positions are not essential to completing localStation, but are
# essential for avoiding missing metadata. They are based on scan 971324

pos base_z_offset -13.537191459600757
pos m1y_offset -15.366825459600758
pos m2_coating_offset 11
pos m2y_offset -22.340825459600758
pos ztable_offset -19.99470545960076

pos pil3_centre_i 239
pos pil3_centre_j 106