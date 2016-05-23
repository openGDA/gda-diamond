#! /bin/bash

export BEAMLINE=i22
. /usr/share/Modules/init/bash

. /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh

mv -f nohup.out nohup.out.0 || true
touch nohup.out

OBJECT_CONSOLE_LOG_FILE="/dls_sw/$BEAMLINE/logs/gda_server_console.$(date +%F_%T).log"
( 
umask 2

/dls_sw/$BEAMLINE/software/gda/bin/gda --config=/dls_sw/$BEAMLINE/software/gda/config --stop logserver || true
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --config=/dls_sw/$BEAMLINE/software/gda/config nameserver
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --config=/dls_sw/$BEAMLINE/software/gda/config eventserver
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --config=/dls_sw/$BEAMLINE/software/gda/config --start logserver
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --config=/dls_sw/$BEAMLINE/software/gda/config --properties=/dls_sw/$BEAMLINE/software/gda/config/properties/java.properties.clientlogserver --start logserver
JAVA_OPTS="-Duser.timezone=GMT -Xms1024m -Xmx8192m -XX:PermSize=256m -XX:MaxPermSize=512m" nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --config=/dls_sw/$BEAMLINE/software/gda/config --debug --verbose objectserver
) >> $OBJECT_CONSOLE_LOG_FILE &

cat >> /dls_sw/$BEAMLINE/logs/gda_server.log <<EOF

gda server restart

EOF

## show log until 'Server initialisation complete' is seen
PIP=/tmp/`basename $0`-$$
mknod $PIP p
tail -n 1 -f /dls_sw/$BEAMLINE/logs/gda_server.log >  $PIP &
awk '{
        if (!/DEBUG/) print ;
        if (/gda.util.ObjectServer - Server initialisation complete.*i22_server_beans/) {
                print "\nAll done, you can start the client now\n" ;
                exit ;
        }
}' < $PIP
rm $PIP

sleep 6
