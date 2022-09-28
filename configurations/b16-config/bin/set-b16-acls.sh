#!/usr/bin/env bash

# Run from e.g. /dls_sw/b16/software/gda_versions/gda_9.13a/workspace_git/gda-diamond.git/configurations

# Check in the correct location
if [[ $(pwd -P) =~ "workspace_git/gda-diamond.git/configurations" ]] && ! [[ $(pwd -P) =~ "b16-config"  ]]; then
    echo "Correct Dir"
else
    echo "In wrong directory!"
    exit 1
fi

# Check this is empty to avoid removing some previously set acls.
acl_info=$(getfacl -R -s -p b16-config/)
if [[ $? != 0 ]]; then
    echo "Command failed."
    exit 1
elif [[ $acl_info ]]; then
    echo "Existing ACLs found, exiting"
    echo "To remove all ACLs run setfacl -R -b b16-config"
    exit 1
else
    echo "No previous ACLs set"
fi

beamline=b16
beamline_staff=b16_staff

GROUP_ACLS="g::rwX,g:gda2:rwX,g:dls_dasc:rwX,g:${beamline_staff}:rwX"
DEFAULT_ACLS="d:u::rwx,d:g::rwx,d:g:gda2:rwx,d:g:dls_dasc:rwx,d:g:${beamline_staff}:rwx,d:m::rwx"

echo "GROUP_ACLS $GROUP_ACLS"
echo "DEFAULT_ACLS $DEFAULT_ACLS"

echo "Setting ACLs on b16-config"
setfacl -bR -m ${GROUP_ACLS},o::r-X,${DEFAULT_ACLS},d:o::r-x b16-config

