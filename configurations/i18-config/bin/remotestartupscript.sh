# GDA 9 remote startup script for i18 beamline control machine

# Get the parent dir of the workspace this script is in
MY_PATH=$(readlink -e ${BASH_SOURCE[0]})
MY_WORKSPACE_PARENT=${MY_PATH%%/workspace_git*}
DLS_CONFIG_SCRIPTS="$MY_WORKSPACE_PARENT/workspace_git/gda-diamond.git/dls-config/bin"

LATCH_SCRIPT="$DLS_CONFIG_SCRIPTS/latch.sh"
RELEASE_VERSION_SCRIPT="$DLS_CONFIG_SCRIPTS/read_release_version.sh"

# Light green text
function lg {
	echo -e "\033[1;32m$1\033[0m"
}

# light red text
function lr {
	echo -e "\033[1;31m$1\033[0m"
}

function help {
	cat 1>&2 <<EOF

Usage: $(basename "${BASH_SOURCE[0]}") [OPTIONS]

Start the gda server in the mode specified by the options, if no target option is specified, the currently
latched one will be used, this is referenced by the launch symlink and initially defaults to release:
At the moment this is:
$(source "$LATCH_SCRIPT")

Required Environment variables:
BEAMLINE     The beamline identifier e.g. i18

OPTIONS:

Target:
$(lg r)elease   Run the most recent released build of the server
$(lg s)napshot  Run the latest Jenkins built snapshot associated with the beamline
$(lg d)evel     Run the most recent export of the server in the beamline workspace

Other:
de$(lg b)ug     Start the server in debug mode waiting for a connection of port 8001
$(lg h)elp      Display this message

N.B. the release, snapshot and devel options are mutually exclusive and will be rejected if more than one is specified

EXAMPLES:

    remotestartupscript.sh

        This will (re)start the latched version of the GDA server (defaults to released).

    remotestartupscript.sh devel debug

        This will initialise the server build last exported from the beamline workspace in debug mode an wait for connection on port 8001 before proceeding

EOF
}

# Exit, displaying supplied error message in red text and help message
function err_msg_exit {
	echo -e "\n$(lr "*** ERROR ***: $1")"
	help
	exit 1
}

## Main routine ##
#
# This script is run as a single command by ssh, so we need to set up our environment
. /usr/share/Modules/init/bash

# Require the BEAMLINE environment variable to have been set
if [[ -z $BEAMLINE ]] ; then
	err_msg_exit "BEAMLINE environment variable not set - GDA server cannot start"
fi

# There is no user or screen to prompt or display pop-ups
export GDA_NO_PROMPT=true

# Adjust memory to handle large scans, -XX:MaxPermSize=128m is retained currently pending further investigation
export JAVA_OPTS="-Xms128m -Xmx4096m  -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

# Resolve the input arguments
if [[ -n "$SSH_ORIGINAL_COMMAND" ]]; then
	ARGS_IN="$SSH_ORIGINAL_COMMAND"
else
	ARGS_IN="$@"
fi

if [[ $ARGS_IN == *"help"* ]]; then
	help
	exit 0
fi

VALID_OPTIONS="|devel|debug|release|snapshot|help|latch|"
for word in $ARGS_IN; do
	if [[ "$VALID_OPTIONS" != *"|$word|"* ]]; then
		err_msg_exit "'$word' is not a valid option"
	fi
done

# Ensure directory containing workspaces exists, and is writable by everyone
USER_WORKSPACE_PARENT=~/scratch/gda_server_user_workspaces
[ -d $USER_WORKSPACE_PARENT ] || mkdir -m 777 $USER_WORKSPACE_PARENT

# Ensure directory containing configs exists, and is writable by everyone
ECLIPSE_RUNTIME_CONFIG_PARENT=~/scratch/gda_server_eclipse_configurations
[ -d $ECLIPSE_RUNTIME_CONFIG_PARENT ] || mkdir -m 777 $ECLIPSE_RUNTIME_CONFIG_PARENT

# Initialise the beamline specific config
BEAMLINE_CONFIG="/dls_sw/$BEAMLINE/software/gda/config"

# Determine the required server application install location an add it to the path:
#
# Default: used the current latched version
#
if [[ "$ARGS_IN" != *"devel"* ]] && [[ "$ARGS_IN" != *"release"* ]] && [[ "$ARGS_IN" != *"snapshot"* ]]; then
	module load gda-server/$BEAMLINE
	$LATCH_SCRIPT                                              # record the current latched state in the log

# One-time run options:
#
# Devel: add the beamline workspace default server location to the path
#
elif [[ "$ARGS_IN" == *"devel"* ]]; then
	
	# Disallow multiple target options along the way
	#
	if [[ "$ARGS_IN" == *"release"* ]] || [[ "$ARGS_IN" == *"snapshot"* ]]; then
		err_msg_exit "Cannot specify two or more target options together; they are mutually exclusive"
	fi
	export PATH="$MY_WORKSPACE_PARENT/server:${PATH}"          # i.e. "module load gda-server devel"
	echo -e "\n\tSetting up GDA 9 SERVER development target"

# Disallow multiple target options along the way
#
elif [[ "$ARGS_IN" == *"snapshot"* ]] && [[ "$ARGS_IN" == *"release"* ]]; then
	err_msg_exit "Cannot specify two or more target options together; they are mutually exclusive"

# Release or Snapshot: module load the appropriate path
#
else
	if [[ "$ARGS_IN" == *"snapshot"* ]]; then
		module load gda-server/snapshot
	else
		source $RELEASE_VERSION_SCRIPT                          # set the RELEASE variable
		module load gda-server/$RELEASE
	fi
fi

# Set server application specifics
SERVER_INSTALL_PATH=$(readlink -f $(dirname $(which gda-server)))
SERVER_INSTALL_DIRNAME=$(basename "$SERVER_INSTALL_PATH")

# Initialise the java startup arguments
application_args="-Dgda.mode=live"

if [[ "$ARGS_IN" == *"debug"* ]]; then
	application_args="$application_args -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=8001"
fi

# Set user workspace and eclipse runtime configuration location (user and server build specific)
USER_WORKSPACE=$USER_WORKSPACE_PARENT/$(whoami)
ECLIPSE_RUNTIME_CONFIG_DIRNAME=$(whoami)-$SERVER_INSTALL_DIRNAME
ECLIPSE_RUNTIME_CONFIG=$ECLIPSE_RUNTIME_CONFIG_PARENT/$ECLIPSE_RUNTIME_CONFIG_DIRNAME

# Add java location to the path
module load java/gda90

# If the server is already running, give it 10 seconds to properly shut down, then restart
RUNNING_SERVER_PID=$(ps -ef | grep [G]da-server | awk '{ print $2 }')
if [[ -n "$RUNNING_SERVER_PID" ]]; then
	$(kill "$RUNNING_SERVER_PID")
	sleep 10
fi

# Assemble the command string
COMMAND="gda-server -data $USER_WORKSPACE -configuration $ECLIPSE_RUNTIME_CONFIG -c $BEAMLINE_CONFIG -vmArgs $application_args"

# and execute it retaining stdin
echo "Starting the GDA Server at $SERVER_INSTALL_PATH/gda-server"
$COMMAND &
