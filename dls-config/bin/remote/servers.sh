# runs the servers locally

#identify install folder and JAVA_HOME
export GDAFOLDER=/dls_sw/$BEAMLINE/software/gda
export GDAVAR=/dls_sw/$BEAMLINE/software/gda_versions/var
export GDALOGS=/dls_sw/$BEAMLINE/software/logs
export GDAMODE=live
export PATH=${GDAFOLDER}/config/bin:${GDAFOLDER}/workspace_git/gda-diamond.git/dls-config/bin:${PATH}

. /usr/share/Modules/init/bash

. /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh
echo "JAVA_HOME=$JAVA_HOME"

#this is needed to ensure the acls work properly
umask 0002

export LOGFILE=$GDALOGS/gda_output_`date +%F-%T`.txt
touch $LOGFILE
rm $GDALOGS/gda_output.txt
ln -s $LOGFILE $GDALOGS/gda_output.txt


export GDA_CONFIGDIR=$GDAFOLDER/config

echo GDAFOLDER=$GDAFOLDER
echo BEAMLINE=$BEAMLINE
SERVER_STARTUP_FILE=$GDAVAR/object_server_startup_server_main; export SERVER_STARTUP_FILE
rm -f $SERVER_STARTUP_FILE

echo "Starting GDA. Output is being logged to $LOGFILE"

export JAVA_OPTS="-Xms128m -Xmx1024m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

nohup python ${GDAFOLDER}/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=$GDA_CONFIGDIR --restart -v --mode=$GDAMODE  nameserver >> $LOGFILE 2>&1 &
sleep 2

nohup python ${GDAFOLDER}/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=$GDA_CONFIGDIR --restart -v --mode=$GDAMODE  logserver >> $LOGFILE 2>&1 &
sleep 2


nohup python ${GDAFOLDER}/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=$GDA_CONFIGDIR --debug -p 8002 --restart -v --mode=$GDAMODE  eventserver >> $LOGFILE 2>&1 &
sleep 2

export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"
#export JAVA_OPTS="$JAVA_OPTS -javaagent:/dls_sw/dasc/jrebel/5.2/jrebel.jar -Drebel.properties=/dls_sw/dasc/jrebel/5.2/jrebel.properties"
#export JAVA_OPTS="$JAVA_OPTS -agentpath:/home/tjs15132/jprofiler8_agent/bin/linux-x64/libjprofilerti.so=port=8849,nowait"
nohup python ${GDAFOLDER}/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=$GDA_CONFIGDIR --debug -p 8001  --restart -v --mode=$GDAMODE objectserver >> $LOGFILE 2>&1 &
echo "Looking for file $SERVER_STARTUP_FILE"
${GDAFOLDER}/workspace_git/gda-diamond.git/dls-config/bin/utils/lookForFile $SERVER_STARTUP_FILE