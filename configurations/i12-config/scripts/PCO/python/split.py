import sys
import Image
import os

print "Image splitter"

dirname = sys.argv[1]
name    =  sys.argv[2]

print "direcoty name is ", dirname
print "image name is ", name


dirlist = os.listdir(dirname)

print "dirlist is ", dirlist

filenumber = 0

for filename in [a for a in dirlist if (a.find(name) >= 0)] :
	print filename

	#load the image in the series
	im = Image.open(os.path.join(dirname,filename))
	
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

