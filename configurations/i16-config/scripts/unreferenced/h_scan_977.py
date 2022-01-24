

#scan hkl [-2.2 0 1] [-2.03 0 1] [0.005 0 0] t 1 checkbeam inctime
#scan hkl [-2.05 0 1] [-1.95 0 1] [0.001 0 0] t 1 checkbeam inctime
#scan hkl [-1.97 0 1] [-1.03 0 1] [0.005 0 0] t 1 checkbeam inctime

#scan hkl [-1.05 0 1] [-0.95 0 1] [0.001 0 0] t 1 checkbeam inctime
#scan hkl [-0.97 0 1] [-0.03 0 1] [0.005 0 0] t 1 checkbeam inctime

#scan hkl [-0.05 0 1] [0.05 0 1] [0.001 0 0] t 1 checkbeam inctime

#scan hkl [0.03 0 1] [0.97 0 1] [0.005 0 0] t 1 checkbeam inctime
#scan hkl [0.95 0 1] [1.05 0 1] [0.001 0 0] t 1 checkbeam inctime

#scan hkl [1.03 0 1] [1.97 0 1] [0.005 0 0] t 1 checkbeam inctime
#scan hkl [1.95 0 1] [2.05 0 1] [0.001 0 0] t 1 checkbeam inctime
#scan hkl [2.03 0 1] [2.2 0 1] [0.005 0 0] t 1 checkbeam inctime





pos eta 10
pos ds [1 1]
# Th2TH Beast!
#define offset
tesffo = 0.5324
piloff = 9.5
SiPeakAtten = 40

pos atten 0

scan th2th [15/2.0+tesffo 15-piloff] [69/2.0+tesffo 69-piloff] [3 6] pil 30 inctime checkbeam

pos atten SiPeakAtten

scan th2th [70/2.0+tesffo 70-piloff] [88/2.0+tesffo 88-piloff] [3 6] pil 30 inctime checkbeam

pos atten 0

scan th2th [88/2.0+tesffo 85-piloff] [121/2.0+tesffo 121-piloff] [3 6] pil 30 inctime checkbeam

pos eta 10.0



#scan hkl [0 -2.2 1] [0 -2.03 1] [0 0.005 0] t 1 checkbeam inctime
#scan hkl [0 -2.05 1] [0 -1.95 1] [0 0.001 0] t 1 checkbeam inctime
#scan hkl [0 -1.97 1] [0 -1.03 1] [0 0.005 0] t 1 checkbeam inctime

#scan hkl [0 -1.05 1] [0 -0.95 1] [0 0.001 0] t 1 checkbeam inctime
#scan hkl [0 -0.97 1] [0 -0.03 1] [0 0.005 0] t 1 checkbeam inctime

#scan hkl [0 -0.05 1] [0 0.05 1] [0 0.001 0] t 1 checkbeam inctime

#scan hkl [0 0.03 1] [0 0.97 1] [0 0.005 0] t 1 checkbeam inctime
#scan hkl [0 0.95 1] [0 1.05 1] [0 0.001 0] t 1 checkbeam inctime

#scan hkl [0 1.03 1] [0 1.97 1] [0 0.005 0] t 1 checkbeam inctime
#scan hkl [0 1.95 1] [0 2.05 1] [0 0.001 0] t 1 checkbeam inctime
#scan hkl [0 2.03 1] [0 2.2 1] [0 0.005 0] t 1 checkbeam inctime


