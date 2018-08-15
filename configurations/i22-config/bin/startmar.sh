#! /bin/bash

export BEAMLINE=i22
. /usr/share/Modules/init/bash

. /dls_sw/i22/software/gda/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh

JAVA_OPTS="-Xms128m -Xmx128m -XX:PermSize=64m -XX:MaxPermSize=128m" /dls_sw/i22/software/gda/bin/gda objectserver  -x /dls_sw/i22/software/gda/config/xml/i22_mar_server.xml --debug --stop
sleep 1
JAVA_OPTS="-Xms128m -Xmx128m -XX:PermSize=64m -XX:MaxPermSize=128m" nohup /dls_sw/i22/software/gda/bin/gda objectserver  -x /dls_sw/i22/software/gda/config/xml/i22_mar_server.xml --debug 
sleep 1
