#killall java
. /usr/share/Modules/init/bash
module load java/gda
#JAVA_OPTS="-Xms1024m -Xmx4096m -XX:PermSize=512m -XX:MaxPermSize=1024m" /dls_sw/b18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --config=/dls_sw/b18/software/gda/config --debug -p 8001 --restart servers

nohup python /dls_sw/b18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/b18/software/gda/config --restart -v --mode=live nameserver &
nohup python /dls_sw/b18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/b18/software/gda/config --restart -v --mode=live logserver &
nohup python /dls_sw/b18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/b18/software/gda/config --debug -p 8002 --restart -v --mode=live eventserver &
export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"
nohup python /dls_sw/b18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/b18/software/gda/config --debug -p 8001 --restart -v --mode=live objectserver &