mode  e2k 1
mode euler 2
mode sp v
#pos energy 8.09503
reflfile Crystal
lattice 5.573 7.534 5.215 90. 90 90.

#need to set the ub matrix
az.setPsi(0.0)
aziref [1 0 0]
reflset 1 2
#
#mode euler 6; level energy 3; level hkl 4

print "hkl now setup!"

#want this to work:
#scan energy 9 10 0.2 psi 5 10 1 hkl [3 1 0] 

#to generate file:
#lattice 5.573 7.534 5.215 90. 90 90
#pos fourcircle [ 66.686 20.44  12.1545 10]
#refladd 1 [4 0 0]
#pos fourcircle [67.976 31.582 12.1105 10]
#pos delta 67.976 eta 31.582 chi 12.1105 phi 10
#refladd 2 [4 1 0]
