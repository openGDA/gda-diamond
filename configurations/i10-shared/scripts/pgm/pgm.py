"""
Copy of Peter Bencocks conversion functions: /dls_sw/i10/scripts/Peter/pgm.py

For use with GDA on I10 at Diamond Light Source
"""

from math import sin, asin # Missing imports

# Calculates energy for given grating density, grating angle, plane mirror angle and offsets
def angles2energy(gd, grang, pmang, groff, pmoff):
    from math import degrees, radians, sqrt
    KE=1.239842012e-3
    pmang-=pmoff
    grang-=groff
    return KE*gd/(sin(radians(2*pmang-grang))-sin(radians(grang)))

# Calculates grating angle for given grating density, energy, cff and grating offset
def enecff2grating(gd, energy, cff, groff):
    from math import degrees, radians, sqrt
    from math import asin
    KE=1.239842012e-3
    d=KE*gd/energy
    a=1-cff*cff
    b=2*cff*cff*d
    c=cff*cff-cff*cff*d*d-1
    e=sqrt(b*b-4*a*c)
    return degrees(asin((b-e)/(2*a)))+groff

# Calculates plane mirror angle for given grating density, energy, cff and offsets
def enecff2mirror(gd, energy, cff, groff, pmoff):
    from math import degrees, radians, sqrt
    KE=1.239842012e-3
    d=KE*gd/energy
    a=1-cff*cff
    b=2*cff*cff*d
    c=cff*cff-cff*cff*d*d-1
    e=sqrt(b*b-4*a*c)
    beta = degrees(asin((b-e)/(2*a)))+groff
    b=-2*d
    c=cff*cff+d*d-1
    alfa = degrees(asin((-b-e)/(2*a)))
    return (alfa+beta-groff)/2+pmoff

# Calculates grating angle for given grating density, energy, mirror angle and offsets
def enemirror2grating(gd, energy, pmang, groff, pmoff):
    from math import degrees, radians, sqrt
    KE=1.239842012e-3
    pmang-=pmoff
    return -degrees(asin(KE*gd/(2*energy*sqrt(1-sin(radians(pmang))*sin(radians(pmang))))))+pmang+groff
