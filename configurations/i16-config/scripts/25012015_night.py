#First scan #494...
#started 4:15am 24/01/15

#[0,0,5]:

pos do do.pil
pos gam 0.5
pos delta 0
hkl_centre=[0,0,5]

pos energy 11.215
pos atten 100
pos hkl(hkl_centre)
# Twin 1
scancn hkl [0.0025, 0.0000, 0.0000] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0000, 0.0000, 0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0025, 0.0000,-0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0025, 0.0000, 0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0000, 0.0025, 0.0000] 801 pil 1 roi2 roi1 checkbeam 

# Twin 2
pos hkl(hkl_centre) 
#pos hkl([0.014+0.125,0.07+0.375,5.008-0.125])
scancn hkl [-0.00125,-0.00375, 0.001250] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [-0.00125, 0.00375,-0.001250] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [-0.00125,-0.00375, 0.003750] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [ 0.00125,-0.00125,-0.000417] 801 pil 1 roi2 roi1 checkbeam

pos energy 11.18
pos hkl(hkl_centre)
# Twin 1





pos energy 11.215
hkl_centre=[1,0,4]
pos hkl(hkl_centre) 
# Twin 1
scancn hkl [0.0000, 0.0000, 0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0025, 0.0000,-0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0025, 0.0000, 0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0000, 0.0025, 0.0000] 801 pil 1 roi2 roi1 checkbeam 

pos energy 11.18
hkl_centre=[1,0,4]
pos hkl(hkl_centre) 
# Twin 1
scancn hkl [0.0000, 0.0000, 0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0025, 0.0000,-0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0025, 0.0000, 0.0025] 801 pil 1 roi2 roi1 checkbeam
scancn hkl [0.0000, 0.0025, 0.0000] 801 pil 1 roi2 roi1 checkbeam 
pos energy 11.215