# GDA 9 remote startup script for i18 beamline control machine

# This script is run as a single command by ssh, so we need to set up our environment
. /usr/share/Modules/init/bash

# Require the BEAMLINE environment variable to have been set
if [ -z $BEAMLINE ] ; then
	echo "ERROR: BEAMLINE environment variable not set - GDA server cannot start" 1>&2
	exit 1
fi

# If the server is already running, give it 10 seconds to properly shut down, then restart 
RUNNING_SERVER_PID=$(ps -ef | grep [G]da-server | awk '{ print $2 }')
if [[ -n "${RUNNING_SERVER_PID}" ]]; then
	$(kill "${RUNNING_SERVER_PID}")
	sleep 10
fi

# There is no user or screen to prompt or display pop-ups
export GDA_NO_PROMPT=true

# Adjust memory to handle large scans, -XX:MaxPermSize=128m is retained currently pending further investigation
export JAVA_OPTS="-Xms128m -Xmx4096m  -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

# Ensure directory containing workspaces exists, and is writable by everyone
USER_WORKSPACE_PARENT=/scratch/gda_server_user_workspaces
[ -d $USER_WORKSPACE_PARENT ] || mkdir -m 777 $USER_WORKSPACE_PARENT

# Ensure directory containing configs exists, and is writable by everyone
ECLIPSE_RUNTIME_CONFIG_PARENT=/scratch/gda_server_eclipse_configurations
[ -d $ECLIPSE_RUNTIME_CONFIG_PARENT ] || mkdir -m 777 $ECLIPSE_RUNTIME_CONFIG_PARENT

# Add the server shared location to the path
module load gda-server/$BEAMLINE

# Set server application specifics
SERVER_INSTALL_DIRNAME=$(basename $(readlink -f $(dirname $(which gda-server))))
SERVER_APPLICATION="gda-server"

# Set user workspace and eclipse runtime configuration location (user and server build specific)
USER_WORKSPACE=$USER_WORKSPACE_PARENT/$(whoami)
ECLIPSE_RUNTIME_CONFIG_DIRNAME=$(whoami)-$SERVER_INSTALL_DIRNAME
ECLIPSE_RUNTIME_CONFIG=$ECLIPSE_RUNTIME_CONFIG_PARENT/$ECLIPSE_RUNTIME_CONFIG_DIRNAME

# Initialise the beamline specific command string components
BEAMLINE_CONFIG="/dls_sw/$BEAMLINE/software/gda/config"

# Initialise the java startup arguments
args="-Dgda.mode=live"
for word in "$@"; do
	if [[ "${word}" == "debug" ]] || [[ ${SSH_ORIGINAL_COMMAND} == "debug" ]]; then
		args="$args -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=8001"
	fi
done

# Add java location to the path
module load java/gda90


# Assemble the command string
COMMAND="$SERVER_APPLICATION -data $USER_WORKSPACE -configuration $ECLIPSE_RUNTIME_CONFIG -c $BEAMLINE_CONFIG -vmArgs $args"

# and execute it retaining stdin 
$COMMAND &
