#!/bin/bash

if [ -f "/etc/profile.d/modules.sh" ]; then
    . /etc/profile.d/modules.sh
fi

. /dls_sw/$BEAMLINE/etc/gda_environment.sh

killall java

JAVA_OPTS="-Xms1024m -Xmx4096m -XX:PermSize=512m -XX:MaxPermSize=1024m" /dls_sw/i08/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --config=/dls_sw/i08/software/gda/config --debug -p 8001 --restart servers
