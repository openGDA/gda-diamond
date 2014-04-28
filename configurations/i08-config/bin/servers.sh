. ${GDAFOLDER}/gda_git/gda-diamond.git/dls-config/bin/loadjava.sh
echo "JAVA_HOME=$JAVA_HOME"

#this is needed to ensure the acls work properly
umask 0002

export LOGFILE=$GDALOGS/gda_output_`date +%F-%T`.txt
touch $LOGFILE
rm $GDALOGS/gda_output.txt
ln -s $LOGFILE $GDALOGS/gda_output.txt

echo GDAFOLDER=$GDAFOLDER
echo BEAMLINE=$BEAMLINE
SERVER_STARTUP_FILE=/tmp/object_server_startup_server_main; export SERVER_STARTUP_FILE
rm -f $SERVER_STARTUP_FILE

echo "Starting GDA. Output is being logged to $LOGFILE"

export JAVA_OPTS="-Xms128m -Xmx1024m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

python ${GDAFOLDER}/gda_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=$GDAFOLDER/gda/config --restart -v --mode=$GDAMODE nameserver > $LOGFILE  &


python ${GDAFOLDER}/gda_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=$GDAFOLDER/gda/config --restart -v --mode=$GDAMODE logserver > $LOGFILE  &


python ${GDAFOLDER}/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=$GDAFOLDER/gda/config --debug -p 8002 --restart -v --mode=$GDAMODE eventserver > $LOGFILE  &

export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"
#export JAVA_OPTS="$JAVA_OPTS -javaagent:/dls_sw/dasc/jrebel/5.2/jrebel.jar -Drebel.properties=/dls_sw/dasc/jrebel/5.2/jrebel.properties"
python ${GDAFOLDER}/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=$GDAFOLDER/gda/config --debug -p 8001 --restart -v --mode=$GDAMODE objectserver > $LOGFILE  &
echo "Looking for file $SERVER_STARTUP_FILE"
$GDAFOLDER/config/bin/lookForFile $SERVER_STARTUP_FILE
