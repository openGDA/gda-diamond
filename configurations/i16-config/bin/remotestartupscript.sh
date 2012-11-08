#!/bin/bash -l
umask 0002
echo Sourcing /dls_sw/$BEAMLINE/etc/${BEAMLINE}.sh
. /dls_sw/$BEAMLINE/etc/${BEAMLINE}.sh

CMD="$SSH_ORIGINAL_COMMAND"
: ${CMD:="$*"}

mv -f nohup.out nohup.out.0 || true
touch nohup.out

touch /dls_sw/i16/logs/gda_client.logs_are_in_workstation_scratch_var_log_folders
(
nohup `dirname $0`/gda logserver $@
nohup `dirname $0`/gda nameserver $@
nohup `dirname $0`/gda eventserver $@
#nohup `dirname $0`/gda --properties=/dls_sw/i16/software/gda/config/properties/live/clientlogserver.properties logserver 
JAVA_OPTS="-XX:MaxPermSize=512m -Xms512m -Xmx4096m" nohup `dirname $0`/gda objectserver --debug -v $@
) &

## show log until 'Server initialisation complete' is seen
PIP=/tmp/`basename $0`-$$
mknod $PIP p
tail -n 1 -f nohup.out > $PIP &
awk '{
        if (!/DEBUG/) print ;
        if (/\[gda.util.ObjectServer\] - Server initialisation complete/) {
                print "\n\033[1;32mAll done, you can start the client now\033[0m\n" ;
                exit ;
        }
}' < $PIP
rm $PIP

sleep 6

