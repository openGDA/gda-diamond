. /usr/share/Modules/init/bash

. /dls_sw/b18/software/gda/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh

#
# restart da.server on b18-xspress0 from this script using ssh
# (13 Jan 2015: I have created a public-private key relationship between gda2@b18-control and b18detector@b18-xspress0 to get this to work)
#

# 9-element:
#ssh b18detector@b18-xspress0 'pkill -9 da.server'
#sleep 65
#ssh b18detector@b18-xspress0 'cd xspress2_9element/; da.server -port=1972 -log' &


# 36 element:
ssh b18detector@b18-xspress1 'pkill -9 da.server'
sleep 65
ssh b18detector@b18-xspress1 'cd xspress2_36element/; da.server -port=1972 -log' &

#
#
#

python /dls_sw/b18/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/b18/software/gda/config --restart -v --mode=live nameserver &
python /dls_sw/b18/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/b18/software/gda/config --restart -v --mode=live logserver &
python /dls_sw/b18/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/b18/software/gda/config --debug -p 8002 --restart -v --mode=live eventserver &
export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"
python /dls_sw/b18/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/b18/software/gda/config --debug -p 8001 --restart -v --mode=live objectserver &
