# This scripts sets limits and spedd for coherent XRD (long detector arm)

#run(xps_config_speed)
xps_setSpeed('delta',0.5)

gam.setUpperGdaLimits(1)
gam.setLowerGdaLimits(-1)
mu.setUpperGdaLimits(1)
mu.setLowerGdaLimits(-1)
delta_no_offset.setUpperGdaLimits(30)
delta_no_offset.setLowerGdaLimits(-5)

# special for Frederic's chamber
#kap.setUpperGdaLimits(10)
#kap.setLowerGdaLimits(-10)
#kth.setUpperGdaLimits(120)
#kth.setLowerGdaLimits(80)
#kphi.setUpperGdaLimits(10)
#kphi.setLowerGdaLimits(-10)
#eta.setUpperGdaLimits(120)
#eta.setLowerGdaLimits(80)

tthp.ccd=70
