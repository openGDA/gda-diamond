# GDA 9 remote startup script for i18 beamline control machine

# This script is run as a single command by ssh, so we need to set up our environment
. /usr/share/Modules/init/bash

runningServerPID=$(ps -ef | grep [G]da-server | awk '{ print $2 }')

# If the server is already running, give it 10 seconds to properly shut down, then restart 
if [[ -n "${runningServerPID}" ]]; then
	$(kill "${runningServerPID}")
	sleep 10
fi

# There is no user or screen to prompt or display pop-ups
export GDA_NO_PROMPT=true

# Adjust memory to handle large scans
export JAVA_OPTS="-Xms128m -Xmx4096m  -XX:MaxPermSize=128m -XX:+DisableExplicitGC"

# Initialise the command string components
install_root="/dls_sw/i18/software/gda"
server_binary="$install_root/server/gda-server"
workspace_loc="$install_root/server/dls-root/workspace"
config_loc="$install_root/workspace_git/gda-dls-beamlines-xas.git/i18"
load_java="$install_root/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh"
args="-Dgda.mode=live"

for word in "$@"; do
	if [[ "${word}" == "debug" ]] || [[ ${SSH_ORIGINAL_COMMAND} == "debug" ]]; then
		args="$args -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=8001"
	fi
done

# We will need java
. $load_java

# Assemble the command string
command="$server_binary -data $workspace_loc -config $config_loc -vmArgs $args"

# and execute it retaining stdin 
$command &
