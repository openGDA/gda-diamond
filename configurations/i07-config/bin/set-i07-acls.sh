#!/usr/bin/env bash

# Run from e.g. /dls_sw/i07/software/gda_versions/gda_9.13a/workspace_git/gda-mt.git/configurations

# Check in the correct location
if [[ $(pwd -P) =~ "workspace_git/gda-diamond.git/configurations" ]] && ! [[ $(pwd -P) =~ "i07-config"  ]]; then
    echo "Correct Dir"
else
    echo "In wrong directory!"
    exit 1
fi

# Check this is empty to avoid removing some previously set acls.
acl_info=$(getfacl -R -s -p i07-config/)
if [[ $? != 0 ]]; then
    echo "Command failed."
    exit 1
elif [[ $acl_info ]]; then
    echo "Existing ACLs found, exiting"
    echo "To remove all ACLs run setfacl -R -b i07-config"
    exit 1
else
    echo "No previous ACLs set"
fi

beamline=i07
beamline_staff=i07_staff

GROUP_ACLS="g::rwX,g:gda2:rwX,g:dls_dasc:rwX,g:${beamline_staff}:rwX"
DEFAULT_ACLS="d:u::rwx,d:g::rwx,d:g:gda2:rwx,d:g:dls_dasc:rwx,d:g:${beamline_staff}:rwx,d:m::rwx"

echo "GROUP_ACLS $GROUP_ACLS"
echo "DEFAULT_ACLS $DEFAULT_ACLS"

echo "Setting ACLs on i07-config/scripts"
setfacl -bR -m ${GROUP_ACLS},o::r-X,${DEFAULT_ACLS},d:o::r-x i07-config/scripts
echo "Setting ACLs on i07-config/lookupTables"
setfacl -bR -m ${GROUP_ACLS},o::r-X,${DEFAULT_ACLS},d:o::r-x i07-config/lookupTables
echo "Setting ACLs on i07-config/servers/main/live/transient.xml"
setfacl -bR -m ${GROUP_ACLS},o::r-X,${DEFAULT_ACLS},d:o::r-x i07-config/servers/main/live/transient.xml

