#! /bin/bash

export BEAMLINE=i05

. /usr/share/Modules/init/bash

. /dls_sw/$BEAMLINE/software/gda/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh

LOGFILE=/dls_sw/$BEAMLINE/logs/gda_server.log

mv -f nohup.out nohup.out.0 || true
touch nohup.out

export GDA_CONFIG=/dls_sw/$BEAMLINE/software/gda/config

( 
/dls_sw/$BEAMLINE/software/gda/bin/gda --stop logserver || true
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --mode=live nameserver 
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --mode=live eventserver 
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --mode=live logserver 
nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --mode=live --properties=/dls_sw/$BEAMLINE/software/gda/config/properties/java.properties.clientlogserver logserver 
JAVA_OPTS="-Xms1024m -Xmx8192m -XX:PermSize=256m -XX:MaxPermSize=512m" nohup /dls_sw/$BEAMLINE/software/gda/bin/gda --mode=live --debug --verbose objectserver 
) &

cat >> $LOGFILE <<EOF

gda server restart

EOF

## show log until 'Server initialisation complete' is seen
PIP=/tmp/`basename $0`-$$
mknod $PIP p
tail -n 1 -f $LOGFILE >  $PIP &
awk '{
        if (!/DEBUG/) print ;
        if (/gda.util.ObjectServer - Server initialisation complete.*server.xml/) {
                print "\nAll done, you can start the client now\n" ;
                exit ;
        }
}' < $PIP
rm $PIP

sleep 6
