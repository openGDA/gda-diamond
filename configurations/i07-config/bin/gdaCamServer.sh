#! /bin/bash

#A shell file that using netcat to setup a server for redirecting the input/output of Pilatus Camserver

cd p2_det

#The path to project-specific resource files to be passed to tvx & camserver
path_to_rc=`pwd`
rm -rf debug.out camdbg.out

# the path to the tvx executable - the path to camserver is derived from this
cd $path_to_rc/programs/tvx


v=`ps a|grep camserver`
echo $v
if [ "`echo $v|cut -d' ' -f 4`" = 'camserver' ]
then
	echo camserver is running - not restarted
elif [ "`echo $v|cut -d' ' -f 5`" = 'camserver' ]
then
	echo camserver is running - not restarted
else
	pushd ./camera/camserver

	# Method 1: Running camserver in an X Terminal, and redirect the output into a logfile,
	# then use netcat to redirect the logfile over network
	xterm -geometry 80x40+20-5 -e "./camserver $path_to_rc 2>&1 | tee /tmp/camserverOutput.txt" &
	tail -f /tmp/camserverOutput.txt | netcat -l -p 5001

	# Method 2: Running camserver and redirect both input/output to different ports
	#netcat -l -p 5000 | ./camserver $path_to_rc | netcat -l -p 5001
	popd
fi
