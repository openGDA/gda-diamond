#!/bin/bash
##check if da server is running

#isRunning=`pidof /usr/local/bin/da.server` # what is this da.server in here?
#isRunning=`/sbin/pidof java`
isRunning=`/home/i18detector/xspress2_9element/da.server`
if [ "$?" ==  "0" ]
then
echo "Da server running"
#stop the da server

# daserver directory changed from
# /etc/init.d
# to
# /home/i18detector/xspress2_9element


/home/i18detector/xspress2_9element/da.server stop
fi
counter=1
#wait for the port to be disconnected
while true
do
let "counter=$counter + 1"
if [ "$counter" == "100" ] 
then
break
fi
##checking if the port is in use
portInUse=`fuser -n tcp 1972`
if [ "$?" ==  "0" ]
then
echo "port still in use"
sleep 1
else
echo "port not in use"
break
fi
done
echo 'starting the da server'
/home/i18detector/xspress2_9element/da.server start
