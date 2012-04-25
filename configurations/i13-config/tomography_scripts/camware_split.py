#!/dls_sw/apps/python/2.6.2/bin/python
#$Id: camware_split.py 214 2012-02-13 15:46:36Z kny48981 $
import sys
import Image
import os

print "Image splitter"

if (len(sys.argv) != 3):
   print len(sys.argv)
   print "usage: %s directory-name base-name" % sys.argv[0]
   print "create projection files in the local directory" 
   sys.exit(0)

dirname = sys.argv[1]
name    =  sys.argv[2]

print "directory name is ", dirname
print "base name is ", name


dirlist = os.listdir(dirname)

#print "dirlist is ", dirlist

filenumber = 0

#for filename in [a for a in dirlist if (a.find(name) >= 0)] :
for num in range(0,100):

	if (num == 0):
	    filename="%s.tif" % name
        else:
	    filename="%s@%04d.tif" % (name,num)
	print num
	print filename


	#load the image in the series

	endflag=0
	try:
	   im = Image.open(os.path.join(dirname,filename))
	except:
	   endflag=1
	
	if (endflag == 0 ):
		try:
			while 1:
				print "seek position ", im.tell()
				print "file number" , filenumber
				im.save("p_%05d.tif"%(filenumber))
				filenumber+=1
				im.seek(im.tell()+1)
		except EOFError:
			print "end of sequence"
			pass # end of sequence

