#!/bin/bash
# runs the servers locally

# module command not working, so instead explicitly give the link for this GDA release
export JAVA_HOME=/dls_sw/apps/java/x64/jdk1.6.0_37/jre
export PATH=$PATH:/dls_sw/apps/java/x64/jdk1.6.0_37/jre/bin

umask 0002

# stop old servers
pkill java

# run the XMAP configuration script
echo "Configure the XMAP/Vortex detector before (re)starting GDA servers..."
/dls_sw/i20/software/gda/bin/vortex_config.sh

# create log file and link to it
export LOGFILE=/dls_sw/i20/logs/gda_output_`date +%F-%T`.txt
touch $LOGFILE
rm /dls_sw/i20/logs/gda_output.txt
ln -s $LOGFILE /dls_sw/i20/logs/gda_output.txt

export SERVER_STARTUP_FILE=/tmp/object_server_startup_server_main
rm -f $SERVER_STARTUP_FILE

echo ""
echo "Now starting GDA servers..."
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
