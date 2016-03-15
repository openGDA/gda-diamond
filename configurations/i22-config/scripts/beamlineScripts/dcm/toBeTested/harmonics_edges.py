import time
import scisoftpy as dnp
from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

harmonics = ((3, 5.2, 8.5701),
             (4, 6.0, 7.54505),
             (5, 7.6, 7.595),
             (6, 8.8, 7.3799),
             (7, 10.4, 7.4349),
             (8, 12.0, 7.525),
             (9, 13.2, 7.345),
             (10, 14.4, 7.24),
             (11, 15.6, 7.12),
             (12, 16.4, 6.8901),
             (13, 16.8, 6.52495),
             (14, 17.6, 6.365),
             (15, 18, 6.08),
             (16, 18.8, 5.95495),
             (17, 19.2, 5.73),
             (18, 19.6, 5.5151),
             (19, 20.0, 5.3298),
             (20, 20.4, 5.155))

hfm_high = 0
hfm_low = 12.2
vfm_high = -4.45
vfm_low = 12.22

for k in range(0,18,1):
    harmonic = harmonics[k][0]
    energy_start = harmonics[k][1]
    gap_start = harmonics[k][2]
    
    
    if energy_start < 10.0:
        pos hfm_y hfm_low
        pos vfm_x vfm_low
    else:
        pos hfm_y hfm_high
        pos vfm_x vfm_low
    
    pos energy energy_start
    pos idgap_mm gap_start
    
    pos finepitch 0
    pos pitch 0
    rscan finepitch -150 150 0.5 d4d1
    inc finepitch -150
    go maxval
    
    for gap in dnp.arange(gap_start+0.01, gap_start-0.026, -0.005):
        pos idgap_mm gap
        setTitle("Harmonic: "+harmonic.__str__()+" Energy: "+energy_start.__str__()+" ID gap: "+gap.__str__())
        scan s2_yplus 1 -1 0.02 d4d1
        pos s2_yplus 1
        filenum = i22NumTracker.getCurrentFileNumber()
        file = open(PathConstructor.createFromDefaultProperty()+"harmonic_shapes_"+time.strftime("%Y-%m-%d")+".dat","a")
        file.write("%d, %.3f , %.4f\n" % (harmonic, energy_start, filenum))