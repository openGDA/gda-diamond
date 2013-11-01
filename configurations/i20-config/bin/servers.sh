#!/bin/bash
# runs the servers locally

. /usr/share/Modules/init/bash
echo "Loading correct Java version..."
module load java/gda830-64
echo $JAVA_HOME

umask 0002

# stop old servers
pkill java

#Select the XSPRESS system required
XSPRESS_ELEMENTS=64
#XSPRESS_ELEMENTS=36
#if [  "$XSPRESS_ELEMENTS" == "64" ];
#then
#	echo ""
#	echo "Stopping current  da.server process on 64 element i20-xspress0..."
#	ssh -i /dls_sw/i20/software/gda/config/daserver.key i20detector@i20-xspress0 'pkill -9 da.server'
#else
#	echo ""
#	echo "Stopping current  da.server process on 36 element i20-xspress1..."
#	ssh -i /dls_sw/i20/software/gda/config/daserver.key i20detector@i20-xspress1 'pkill -9 da.server'
#fi


# run the XMAP configuration script
#echo ""
#echo "Configure the XMAP/Vortex detector before (re)starting GDA servers..."
#/dls_sw/i20/software/gda/bin/vortex_config.sh

#if [  "$XSPRESS_ELEMENTS" == "64" ];
#then
#	echo ""
#	echo "Will now sleep for 30 seconds for port 1972 to become available on da.server machine..."
#	sleep 30
#	echo "Restarting da.server on 64 element xspress control machine..."
#	ssh -i /dls_sw/i20/software/gda/config/daserver.key i20detector@i20-xspress0 'cd xspress2_64element/; da.server -port=1972 -log' &
#else
#	echo "Will now sleep for 30 seconds for port 1972 to become available on da.server machine..."
#	sleep 30
#	echo "Restarting da.server on 36 element xspress control machine..."
#	ssh -i /dls_sw/i20/software/gda/config/daserver.key i20detector@i20-xspress1 'cd xspress2_36element/; da.server -port=1972 -log' &
#fi
#echo "Xspress system restarted."

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
echo "Waiting for GDA servers to start... (looking for file $SERVER_STARTUP_FILE on $THIS_MACHINE)"
echo "GDA server output is being logged to /dls_sw/i20/logs/gda_output.txt"
/dls_sw/i20/software/gda/config/bin/lookForFile $SERVER_STARTUP_FILE
echo ""
echo "Servers have initialised; you may start a GDA client now."
