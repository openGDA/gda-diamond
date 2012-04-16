# runs the servers locally

#identify install folder and JAVA_HOME
source /dls_sw/i13-1/etc/i13-1_profile.sh

#this is needed to ensure the acls work properly
umask 0002

export LOGFILE=$GDALOGS/gda_output_`date +%F-%T`.txt
touch $LOGFILE
rm $GDALOGS/gda_output.txt
ln -s $LOGFILE $GDALOGS/gda_output.txt

echo GDAFOLDER=$GDAFOLDER
echo BEAMLINE=$BEAMLINE

SERVER_STARTUP_FILE=$GDAVAR/object_server_startup_server_main; export SERVER_STARTUP_FILE
rm -f $SERVER_STARTUP_FILE

echo "Starting GDA. Output is being logged to $LOGFILE"

export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

echo nohup ${GDAFOLDER}/plugins/uk.ac.gda.core/bin/gda  --smart --trace --config=$GDAFOLDER/$BEAMLINE-config --debug -p 8001 --restart -v --mode=$GDAMODE servers > $LOGFILE 2>&1 &
nohup ${GDAFOLDER}/plugins/uk.ac.gda.core/bin/gda  --smart --trace --config=$GDAFOLDER/$BEAMLINE-config --debug -p 8001 --restart -v --mode=$GDAMODE servers > $LOGFILE 2>&1 &
echo "Looking for file $SERVER_STARTUP_FILE"
$GDAFOLDER/$BEAMLINE-config/bin/lookForFile $SERVER_STARTUP_FILE
