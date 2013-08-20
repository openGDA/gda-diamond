#! /usr/bin/env python

import subprocess
import os, sys, getpass
import tempfile

import time
import random
import string

import mimetypes
import httplib

import Image, ImageTk, ImageOps
import Tkinter

#---------------------------------------------------

def eLogPost(title='Comments from I06', content='Simple log with image attached', userID='gda', logID='BLI06',groupID='BLI06-USER',entryType='41',imageFiles=[]):

	#eLog URL

	host = 'rdb.pri.diamond.ac.uk'
#	url ='/devl/php/elog/cs_logentryext_bl.php'
	url='/php/elog/cs_logentryext_bl.php'

	data={	'txtTITLE'      : title, 
		'txtCONTENT'    : content,
		'txtLOGBOOKID'  : logID,
		'txtGROUPID'    : groupID,
		'txtENTRYTYPEID': entryType,
		'txtUSERID'     : userID,
		}

#	files={	'userfile1' : 'b.png',
#		'userfile2' : 'a.jpg',
#		'userfile3' : 'a.jpg' }

	files = dict([('userfile%s'%(n+1), imageFiles[n]) for n in range(len(imageFiles))  ])

	conn=httplib.HTTPConnection(host)

	conn.request("POST", url, *encodeMultipartFormData(data, files) )

	response = conn.getresponse()

	print response.status, response.reason
	data = response.read()
	print data

	conn.close()
	
	result=False;
	if response.status in range(200, 209):
		result= True;

	return result;



def random_string (length):
    return ''.join (random.choice (string.letters) for ii in range (length + 1))

def encodeMultipartFormData(data, files):
    boundary = random_string (30)

    def get_content_type (filename):
    	return mimetypes.guess_type (filename)[0] or 'application/octet-stream'

    lines = []
    for k,v in data.iteritems():
	tt=('--%s'%boundary, 'Content-Disposition: form-data; name="%s"'%k, '', str(v))
	lines.extend(tt);

    for f,filename in files.iteritems():
    	tt=('--' + boundary, 'Content-Disposition: form-data; name="%s"; filename="%s"'%(f, filename),'Content-Type: %s'%get_content_type(filename), '', open (filename, 'rb').read ())
	lines.extend(tt);

    lines.extend (('--%s--' % boundary, ''))

    body = '\r\n'.join (lines)

    headers = {'content-type': 'multipart/form-data; boundary=' + boundary,
               'content-length': str (len (body))}

    return body, headers


def eLogButtonCommand():
	title=titleText.get('1.0', 'end');
	print title; 

	msg=text.get('1.0', 'end');
	print msg;

	content= '<!DOCTYPE html> <html> <body><h1> %s </h1> <p> %s </body></html>' %(title, msg)

	userID=getpass.getuser()
	if userID.endswith('user') or userID.endswith('detector'):
		userID='gda'

	logID='BLI06'
	groupID='BLI06-USER'
	entryType='41';
	imageFiles=[tmpImageFileName];


	#eLogPost(title, content);
	result=eLogPost(title, content, userID, logID, groupID, entryType, imageFiles);
	if result:
#		subprocess.call( ["rm", "-f", tmpImageFileName] )
		sys.exit("Message with Image successfully logged.")


tmpImageFileName=os.path.join(tempfile.gettempdir(), time.strftime("%Y_%m_%d-%H_%M_%S.png", time.gmtime()) );
a=subprocess.call( ["import", tmpImageFileName] )
im=Image.open(tmpImageFileName)

#To resize the image while keep the aspect ratio
maxWidth, maxHeight=600, 400
im.thumbnail((maxWidth, maxHeight), Image.ANTIALIAS);
#ratio=min(1.0*maxWidth/im.size[0], 1.0*maxHeight/im.size[1]);
#im=im.resize( [int(ratio* s) for s in im.size], Image.ANTIALIAS);

root=Tkinter.Tk()
root.title("Grab2log");
tkimage=ImageTk.PhotoImage(im)


Tkinter.Label(text='Screen Captured:').pack(side=Tkinter.TOP)
imageLabel=Tkinter.Label(root, image=tkimage)
imageLabel.pack();

Tkinter.Label(text='Title:').pack(side=Tkinter.TOP, padx=10, pady=10)
titleText=Tkinter.Text(root, height=1, wrap='word')
titleText.insert(Tkinter.INSERT, "Image grabbed from screen on: " + time.asctime())
titleText.pack();

Tkinter.Label(text='Comments:').pack(side=Tkinter.TOP)

text=Tkinter.Text(root, height=5, wrap='word')
text.pack();

eLogButton=Tkinter.Button(root, text="eLog", command=eLogButtonCommand)
eLogButton.pack(side=Tkinter.LEFT, padx=8,pady=8)

quitButton=Tkinter.Button(root, text="Exit", command=quit)
quitButton.pack(side=Tkinter.RIGHT)

root.mainloop()



