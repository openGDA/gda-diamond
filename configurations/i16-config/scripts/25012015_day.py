#First scan #493941
#started 1:45pm 24/01/15

pos energy 11.215

pos hkl([1,0,5])
pos atten 100

scancn hkl [0.005,0.000,0.000] 365 pil 1 roi2 roi1 checkbeam
scancn hkl [0.000,0.000,0.005] 365 pil 1 roi2 roi1 checkbeam
scancn hkl [0.005,0.000,-0.005] 365 pil 1 roi2 roi1 checkbeam
scancn hkl [0.005,0.000,0.005] 365 pil 1 roi2 roi1 checkbeam
pos hkl([0,0.5,5])
scancn hkl [0.000,0.005,0.000] 183 pil 1 roi2 roi1 checkbeam
pos hkl([1,0.5,5])
scancn hkl [0.000,0.005,0.000] 183 pil 1 roi2 roi1 checkbeam


pos atten 100

#pos hkl([0.014+0.125,0.07+0.375,5.008-0.125])
#scancn hkl [-0.0025,-0.0075,0.0025] 101 pil 1 roi2 roi1 checkbeam

#pos hkl([0.014-0.125,0.07+0.375,5.008-0.125])
#scancn hkl [0.0025,-0.0075,0.0025] 101 pil 1 roi2 roi1 checkbeam
#
#pos hkl([0.014+0.125,0.07+0.375,5.008-0.375])
#scancn hkl [-0.0025,-0.0075,0.0075] 101 pil 1 roi2 roi1 checkbeam

#pos hkl([0.014-0.125,0.07+0.125,5.008+0.0417])
#scancn hkl [0.0025,-0.0025,-0.00083] 101 pil 1 roi2 roi1 checkbeam


