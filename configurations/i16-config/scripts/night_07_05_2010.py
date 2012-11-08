#138970-end 139075 (error)
#139076-stop at 87 
# try to stop processing images methods were changed!!!!
# restart at 139093-96
#restart at 139098
mode euler 1
ppoff=0.01554

#hkllist=[[0,0,4],[0,2,4],[0.0154,-1.9985,4.00070],[2.0004,0.0076,3.9998],[-2,0,4],[1,1,3],[1,-1,3],[-1,1,3],[1,1,3],[-1,-1,3],[0,0,2]]
#hkllist=[[0,1,2],[0,-1,2],[1,0,2],[-1,0,2],[2.0004,0.0076,3.9998],[-2,0,4],[1,1,3],[1,-1,3],[-1,1,3],[1,1,3],[-1,-1,3],[0,0,2]]

hkllist=[[0,2,3],[0,-2,3],[2,0,3],[-2,0,3],[1,2,3],[-1,2,3],[1,-2,3],[-1,-2,3],[2,1,3],[-2,1,3],[2,-1,3],[-2,-1,3],[0,-1,2],[1,0,2],[-1,0,2]]
#hkllist.append([0,1,2])
#hkllist.append([0,-1,2])
#hkllist.append([1,0,2])
#hkllist.append([-1,0,2])
hkllist.append([1,1,2])
hkllist.append([1,-1,2])
hkllist.append([-1,1,2])
hkllist.append([-1,-1,2])

print hkllist


for iii in hkllist:
	pos energy 7.07
	pos atten 60
	pos hkl iii
	scancn eta 0.006 81 checkbeam pil 1 
	go maxpos
	hkl1=hkl()
	pos ppa111 [en() -ppoff]
	scan energy 7.07 7.15 0.001 hkl hkl1 ppa111 [7.07 -ppoff] [0.001 0] pil 1 checkbeam
	pos ppa111 [en() +ppoff]
	scan energy 7.07 7.15 0.001 hkl hkl1 ppa111 [7.07 +ppoff] [0.001 0] pil 1 checkbeam
	scancn eta 0.01 81 checkbeam pil 1
	

for iii in hkllist:
	pos energy 7.07
	pos atten 60
	pos hkl iii
	scancn eta 0.006 81 checkbeam pil 1 
	go maxpos
	hkl1=hkl()
	pos ppa111 [en() -ppoff]
	scan energy 7.07 7.15 0.001 hkl hkl1 ppa111 [7.07 -ppoff] [0.001 0] pil 1 checkbeam
	pos ppa111 [en() +ppoff]
	scan energy 7.07 7.15 0.001 hkl hkl1 ppa111 [7.07 +ppoff] [0.001 0] pil 1 checkbeam
	scancn eta 0.01 81 checkbeam pil 1 
	
