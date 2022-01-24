'''
Summary of required Scannables from Sandeep's requirements document:

magmode

magx
magy
magz

magrho
magth
magphi

magspherical

magtemp1
magtemp2


Examples:

set magnet mode:
>>> pos magmode uniaxialx

in uniaxialz mode, set the magnitude of the z field:
>>> pos mgz -6

scan z:
>>> scan magz -6 6 1 ca61sr 1

in cubic mode, set all three axis field values:
>>> pos magx1
>>> pos magy 1
>>> pos magz 1

Setting the magnet values in spherical mode is more complicated,
and requires transforming rho, theta, and phi values to the corresponding x, y, and z values.
The user interface for setting the field in spherical mode will use commands such as:
>>> pos magmode spherical
>>> pos magrho 1
>>> pos magth 30
>>> pos magphi 30
This will produce a filed in the positive xyz quadrant of magnitude 1T
at 30 degrees to the y and z axes.

Each of these motors should be scannable:
>>> scan magth 0 90 1 ca61sr 1

Define a single scannable motor to define the magnetic field in spherical mode:
>>> pos magspherical [1, 30, 30]

Scan the magspherical motor:
>>> scan magspherical [1, 30, 30] [-1, -30, -30] 0.1 0 0 ca61sr 1
This moves the field from [1, 30, 30] to [-1, -30, -30] 
along the straight line joining the two points in 21 (?) steps. 

set the sample chamber temperature
pos magtemp1 250

monitor the second temperature
>>> magtemp2





'''
