#!/bin/bash
# This script is only invoked when user gda2 ssh's to the control machine. It should be invoked either directly or sourced via a
# corresponding script from the beamline's config area. It relies on the config link to indicate the location of the beamline's gda script.

# As the calling script will be triggered by an entry in gda's ~/.ssh/authorized_keys as a single command, we need to set up our environment
#
# See http://stackoverflow.com/questions/216202/why-does-an-ssh-remote-command-get-fewer-environment-variables-then-when-run-man
. /usr/share/Modules/init/bash

# There will be no user or screen to prompt or display pop-ups so disable these
export GDA_NO_PROMPT=true

# Set an environment variable to indicate we came through the remote startup script, so that we can error if we attempt to do this recursively
export GDA_IN_REMOTE_STARTUP=true

[[ -n "${SSH_ORIGINAL_COMMAND:-}" ]] && operation="${SSH_ORIGINAL_COMMAND}" || operation=restart

my_location="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
config_bin_location="${my_location}/../../../../config/bin"                      # Unless the standard config locations change in which case modify accordingly

${config_bin_location}/gda --${operation} --mode=live servers < /dev/null > /dev/null 2>&1  # should stop the ssh command that calls this script failing to return
