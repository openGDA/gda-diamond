#!/bin/bash -l

################################################################################
##### IMPORTANT NOTE:
#####
##### While this file is present in both i06 and i06-1 config/bin folders, only
##### the one in /dls_sw/i06/software is actually run when gdaservers ssh's to
##### the i06-control machine.
#####
################################################################################

. /usr/share/Modules/init/bash
. /etc/profile.d/beamline.sh

echo BEAMLINE defaults to $BEAMLINE

BEAMLINE=$SSH_ORIGINAL_COMMAND
CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

echo BEAMLINE now set by SSH_ORIGINAL_COMMAND to $SSH_ORIGINAL_COMMAND

export GDA_MODE=$BEAMLINE
# Since i06-1 runs this from i06, we need a GDA_ROOT based on $BEAMLINE
#      GDA_ROOT must also be set *before* gda_setup_env is run.
#export GDA_ROOT=$(readlink -f $(dirname $0)/../../../../..)
export GDA_ROOT=$(readlink -f /dls_sw/$BEAMLINE/software/gda)
echo GDA_ROOT=$GDA_ROOT

. $GDA_ROOT/workspace_git/gda-mt.git/configurations/mt-config/bin/gda_setup_env gda_servers_output

GDA_VAR=$(readlink -f $GDA_ROOT/../var)
OBJECT_SERVER_STARTUP_FILE=$GDA_VAR/object_server_startup_server_$BEAMLINE
rm -f $OBJECT_SERVER_STARTUP_FILE

umask 0002 # Some voodoo copied from GDA-mt/configurations/i16-config/bin/remotestartupscript.sh at d024aae
# This should fix a problem where sub-directories created in a visit folder end up
# with a different mask to the default.

# Setting XX:MaxPermSize fixes the reset_namespace problem (due to Jython class leakage)
export JAVA_OPTS="-Dgda.deploytype=1 -XX:MaxPermSize=1024m"

#GDA_CORE_SCRIPT_OPTIONS="--headless servers --debug"
GDA_CORE_SCRIPT_OPTIONS="-v --headless servers"

ARGS="--properties $GDA_CONFIG/properties/java.properties_$GDA_MODE"
ARGS="--jacorb     $GDA_CONFIG/properties/jacorb_$GDA_MODE                $ARGS"
ARGS="--jca        $GDA_CONFIG/properties/JCALibrary.properties_$GDA_MODE $ARGS"
ARGS="--vardir     $GDA_VAR                                               $ARGS"
ARGS="--logsdir    /dls_sw/$BEAMLINE/logs                                 $ARGS"

if [ "$BEAMLINE" = "i06-1" ]; then
  ARGS="--nsport 6701 --debugport=8010                                    $ARGS"
fi

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
