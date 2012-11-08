from math import pi

# Speed of light in vacuum
clight = 299792458 # [m.s-1]
# electric constant
epsilon0 = 8.854187817e-12 # F m-1
#magnetic constant
mu0 = 4*pi*1e-7
# vacuum impedance [Ohm]
Z0 = 377

# electron properties
emass = 9.1093826e-31 #[kg]
echarge = 1.60217353e-19 #[C]
#rest mass [MeV]
mc2 = emass*clight**2/echarge*1e-6
# classical radius
eradius = echarge**2/clight**2/(4*pi*epsilon0*emass)*1e10 #[A]

# Plank constant
hPlank = 6.6260693e-34 # J s
hPlankeV = 4.13566743e-15 # eV s
hbar = 1.05457168e-34 # J s
hbareV = 6.58211915e-16 # eV s

# conversion factor from K
# conversion factor E[keV]*lambda[A] =12.3984
keV2A = hPlankeV*clight*1e7

# Atomic unit of mass (1/12 of Carbone12)
aum = 1.66053886e-27 # [kg]
