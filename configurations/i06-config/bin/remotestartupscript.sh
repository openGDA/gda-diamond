#!/bin/bash -l

. /usr/share/Modules/init/bash
. /etc/profile.d/beamline.sh

echo BEAMLINE defaults to $BEAMLINE
echo SSH_ORIGINAL_COMMAND = $SSH_ORIGINAL_COMMAND

BEAMLINE=$SSH_ORIGINAL_COMMAND
CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

SOFTWAREFOLDER=dls_sw; export SOFTWAREFOLDER
#OBJECT_SERVER_STARTUP_FILE=/$SOFTWAREFOLDER/$BEAMLINE/software/gda_versions/var/object_server_startup_server_main
OBJECT_SERVER_STARTUP_FILE=/tmp/object_server_startup_server_i06
rm -f $OBJECT_SERVER_STARTUP_FILE

export GDA_MODE=$BEAMLINE
export GDA_ROOT=$(readlink -f $(dirname $0)/../../../../..)
. $GDA_ROOT/workspace_git/gda-mt.git/configurations/mt-config/bin/gda_setup_env gda_servers_output

umask 0002 # Some voodoo copied from GDA-mt/configurations/i16-config/bin/remotestartupscript.sh at d024aae
# This should fix a problem where sub-directories created in a visit folder end up
# with a different mask to the default.

# Setting XX:MaxPermSize fixes the reset_namespace problem (due to Jython class leakage)
export JAVA_OPTS="-Dgda.deploytype=1 -XX:MaxPermSize=1024m"

GDA_CORE_SCRIPT_OPTIONS="--headless servers --debug"

# i06 & i06-1 all share the same i06-config directory, so override the one from gda_setup_env
export GDA_CONFIG=$GDA_ROOT/workspace_git/gda-mt.git/configurations/i06-config

ARGS="--properties $GDA_CONFIG/properties/java.properties_$GDA_MODE"
ARGS="--jacorb     $GDA_CONFIG/properties/jacorb_$GDA_MODE                $ARGS"
ARGS="--jca        $GDA_CONFIG/properties/JCALibrary.properties_$GDA_MODE $ARGS"
ARGS="--vardir     $GDA_ROOT/../var                                       $ARGS"
ARGS="--logsdir    /dls_sw/$BEAMLINE/logs                                 $ARGS"

echo  $GDA_CORE_SCRIPT $GDA_CORE_SCRIPT_OPTIONS $ARGS
echo  $GDA_CORE_SCRIPT $GDA_CORE_SCRIPT_OPTIONS $ARGS >> $GDA_CONSOLE_LOG
nohup $GDA_CORE_SCRIPT $GDA_CORE_SCRIPT_OPTIONS $ARGS >> $GDA_CONSOLE_LOG  2>&1 &

echo "Waiting for server startup completion:" $OBJECT_SERVER_STARTUP_FILE
# look for the output file which will tell us when the servers have started
while true; do
  if [ -r $OBJECT_SERVER_STARTUP_FILE ]; then
        echo .
        rm -f $OBJECT_SERVER_STARTUP_FILE
        exit 0
  fi

  sleep 1
  echo -n .
done
