# get file information using os.stat()
# tested with Python24 vegsaeat 25sep2006
import os
import stat # index constants for os.stat()
import time
from time import sleep;


def fileInfo(file_name):
	file_stats = os.stat(file_name);
	# create a dictionary to hold file info
	file_info = {
				'fname': file_name,
				'fsize': file_stats [stat.ST_SIZE],
				'f_lm': time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(file_stats[stat.ST_MTIME])),
				'f_la': time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(file_stats[stat.ST_ATIME])),
				'f_ct': time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(file_stats[stat.ST_CTIME]))
				}
	print "file name = %(fname)s" % file_info
	print "file size = %(fsize)s bytes" % file_info
	print "last modified = %(f_lm)s" % file_info
	print "last accessed = %(f_la)s" % file_info
	print "creation time = %(f_ct)s" % file_info
	print
	if stat.S_ISDIR(file_stats[stat.ST_MODE]):
		print "This a directory"
	else:
		print "This is not a directory"
	print
	print "A closer look at the os.stat(%s) tuple:" % file_name
	print file_stats
	print
	print "The above tuple has the following sequence:"
	print """st_mode (protection bits), st_ino (inode number),
		st_dev (device), st_nlink (number of hard links),
		st_uid (user ID of owner), st_gid (group ID of owner),
		st_size (file size, bytes), st_atime (last access time, seconds since epoch),
		st_mtime (last modification time), st_ctime (time of creation, Windows)"""
		
def fileExists(fileName, numberOfTry):
	result = False;

	for i in range(numberOfTry):
		if (not os.path.exists(fileName)) or (not os.path.isfile(fileName)):
			print "File does not exist on try " + str(i+1);
			#check again:
			sleep(1);
			os.system("ls -la " + fileName);
		else:
			#To check the file size non zero
			fsize = os.stat(fileName)[stat.ST_SIZE];
			print "File exists on try " + str(i+1) + " with size " + str(fsize);
			if fsize == 0L:
				sleep(1);
				continue;
			#The file seems exist with some content inside. Double check to make sure it's available
			try:
				tf = open(fileName,"rb");
				tf.close();
				result = True;
				break;
			except:
				print "There are something wrong on the file system !!!"
				raise Exception("There are something wrong on the file system !!!");
	return result;
		