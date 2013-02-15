# runs the servers locally
. /usr/share/Modules/init/bash
export IS_64_BIT=`uname -a | grep _64 | wc -l`
if [ $IS_64_BIT==1 ]; then less 
       module load java/6u37-64
else
       module load java/6u37-32
fi


umask 0002

# stop old servers
pkill java
#/dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --stop objectserver
#/dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --stop eventserver
#/dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --stop nameserver

# create log file and link to it
export LOGFILE=/dls_sw/i20/logs/gda_output_`date +%F-%T`.txt
touch $LOGFILE
rm /dls_sw/i20/logs/gda_output.txt
ln -s $LOGFILE /dls_sw/i20/logs/gda_output.txt

SERVER_STARTUP_FILE=/tmp/object_server_startup_server_main; export SERVER_STARTUP_FILE
rm -f $SERVER_STARTUP_FILE

#nohup /dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --config=/dls_sw/i20/software/gda/config --mode=live --debug -p 8001 --profiler --restart servers > $LOGFILE 2>&1 &


nohup python /dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/i20/software/gda/config --restart -v --mode=live nameserver > $LOGFILE 2>&1 &


nohup python /dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/i20/software/gda/config --restart -v --mode=live logserver > $LOGFILE 2>&1 &


nohup python /dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/i20/software/gda/config --debug -p 8002 --restart -v --mode=live eventserver > $LOGFILE 2>&1 &

export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

nohup python /dls_sw/i20/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/i20/software/gda/config --debug -p 8001 --restart -v --mode=live objectserver > $LOGFILE 2>&1 &


export THIS_MACHINE=`uname -n`
echo ""
echo "Waiting for GDA servers to start (looking for file $SERVER_STARTUP_FILE on $THIS_MACHINE)"
echo "GDA server output is being logged to /dls_sw/i20/logs/gda_output.txt"
/dls_sw/i20/software/gda/config/bin/lookForFile $SERVER_STARTUP_FILE
echo ""
echo "Servers have initialised; you may start a GDA client now."
