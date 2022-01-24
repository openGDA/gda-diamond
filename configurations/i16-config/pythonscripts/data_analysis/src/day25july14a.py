from dlstools import dataloader
path='/dls/i16/data/2014/cm4968-3/'
d=dataloader.dlsloader(path+'%i.dat')

goodscns=[]
npts=[]
rc=[]
scans=range(458468,458601+1)
for scan in scans:
    try:
        d(scan)
        if min(d.rc)>3.0 and len(d.rc==500):
            goodscns+=[scan]
        npts+=[len(d.rc)]
        rc+=[mean(d.rc)]
    except:
        print '=== Scan missing'
plot(rc)
#132 scans in total
#rc variees from 20mA at start to ~ 5 mA
#goodscns=[458468, 458469, 458470, 458471, 458472, 458473, 458474, 458475, 458476, 458477, 458484, 458485, 458486, 458487, 458488, 458489, 458490, 458491, 458492, 458493, 458494, 458495, 458496, 458497, 458498, 458499, 458500, 458501, 458502, 458503, 458504, 458505, 458506, 458507, 458508, 458509, 458510, 458511, 458512, 458513, 458514, 458515, 458516, 458517, 458518, 458519, 458520, 458521, 458522, 458523, 458524, 458525, 458526, 458527, 458528, 458529, 458530, 458531, 458532, 458533, 458534, 458535, 458536, 458537, 458538, 458539, 458540, 458541, 458542, 458543, 458544, 458545, 458546, 458547, 458548, 458549, 458550, 458551, 458552, 458553, 458554, 458555, 458556, 458557, 458558, 458559, 458560, 458561, 458562, 458563, 458564, 458565, 458566, 458567, 458568, 458569, 458570, 458571, 458572, 458573, 458574, 458575, 458576, 458577, 458578, 458579, 458580, 458581, 458582, 458583, 458584, 458585, 458586, 458587, 458588, 458589, 458590, 458591, 458592, 458593, 458594, 458595, 458596, 458597, 458598, 458599, 458600, 458601]
# next: analyse these 132 files




#datadir('/dls/i16/data/2014/cm4968-3/')
#latt([3.567])
#pilatus1_multi.driver.numberOfImagesPerCollection = 200

#pos pil100kgain 2
#pos pil100kthresh 4

#scan x 1 2 1 pilatus1_multi .00001

#reffile('PDC_July_14')
#>>>showref()
#key       h           k           l          Energy         psi        phi         chi         eta           mu       delta       gamma       alpha        beta
#004      0.0000      0.0000      4.0000     14.9450     71.4800    118.0000      4.9850     28.7432      0.0000     55.4405      0.0000     -5.5490     25.3817
#400      4.0000      0.0000      0.0000     14.9450     37.3013     28.0000     91.2500     22.7964      0.0000     55.4405      0.0000    -13.3380     56.8456
#>>>ubm('004','400')
#array('d', [0.006111200831618776, 0.2453425150089657, -0.13551567361687908, -0.024457024553453274, 0.13549764082778765, 0.24420695633511563, 0.2792119292164159, 0.006498761539301977, 0.024356907112108497])
#>>>hkl
#hkl : h: 0.0000 k: -0.0000 l: 4.0000

#ic1 2.02

#sinth=sin(delta()*pi/180)
#dth1=2.5*pi/180
#dth=dth1**2/2/sinth
#dthdeg=dth*180/pi


#etazero=28.7391

#pilatus1_multi.driver.numberOfImagesPerCollection = 200
#
#pos eta etazero+0.0662
#pos atten 0
#for ii in range(1):
#458468
#crashed 458477
#restart 458478 sun 27 july 10:30 - beam lost during first scan
#restart 458484
#restart 458502 - reduce checkbeam min to 0.5
#458589 checkbeam reduced to 0.3 (rc down to 4.6 mA)
#crashed #458601
#end

#while True:
#    pos atten 0
#    pos x1 1
#    checkbeam
#    scan x 1 500 1 checkbeam pilatus1_multi .00001
#    pos x1 0
