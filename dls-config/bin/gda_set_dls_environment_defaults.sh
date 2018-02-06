#!/bin/bash
# Establishes defaults for installation that follow the Diamond Light Source folder structure
# Expects a single parameter specifying what the beamline name should be set to and checks if $BEAMLINE matches it

facility_here_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export  GDA_WORKSPACE_PARENT=$(readlink -f ${facility_here_dir}/../../../..)
        GDA_WORKSPACE_GIT_NAME=$(basename $(readlink -f ${facility_here_dir}/../../..))  # will normally be "workspace_git", will at least end with "_git".

if [[ ! -L ${GDA_WORKSPACE_PARENT}/config ]] || [[ ! -d ${GDA_WORKSPACE_PARENT}/config ]]; then
	echo >&2 "ERROR: Cannot start; a valid config link pointing to a valid configuration folder must exist in the root folder of the deployment."
	exit 1
fi

export GDA_INSTANCE_CONFIG_rel=config
export    GDA_GROUP_CONFIG_rel=${GDA_WORKSPACE_GIT_NAME}/gda-core.git/no-group
export GDA_FACILITY_CONFIG_rel=${GDA_WORKSPACE_GIT_NAME}/gda-diamond.git/dls-config
export     GDA_CORE_CONFIG_rel=${GDA_WORKSPACE_GIT_NAME}/gda-core.git/core-config

# Careful use of parameter expansion replacement formats to check for empty or null BEAMLINE and give a useful error message
# Allows the actual value of $BEAMLINE to be compared to that expected, passed in and set by the originating gda script
if [[ "${BEAMLINE:-}" != "$1" ]]; then
    if [[ "${BEAMLINE:+set}" == "set" ]]; then
        error_message="set to \"${BEAMLINE}\""
    elif [[ "${BEAMLINE+empty}" == "empty" ]]; then
        error_message="empty"
    else
        error_message="not set"
    fi
    echo >&2 "Failed to run GDA for the $1 beamline - the BEAMLINE environment variable is ${error_message}"
    echo >&2 "BEAMLINE must be set to \"$1\" to work with this GDA configuration"
    exit 1
fi

# For GDA installations with multiple end stations GDA_INSTANCE_NAME can be used to distinguish them
# from the overall BEAMLINE setting in client selection, logs and user messaging.

export GDA_INSTANCE_NAME=${BEAMLINE}        # default setting for single end station installations

export  GDA_CLIENT=${GDA_WORKSPACE_PARENT}/client/gda-${GDA_INSTANCE_NAME}

export GDA_STATUS_PORT=19999 # Used to check when the server has started 
