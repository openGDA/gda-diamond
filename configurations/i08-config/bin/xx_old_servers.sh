. /usr/share/Modules/init/bash

. /dls_sw/i08/software/gda/workspace_git/gda-diamond.git/dls-config/bin/loadjava.sh

python /dls_sw/i08/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/i08/software/gda/config --restart -v --mode=live nameserver &
python /dls_sw/i08/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda  --smart --trace --config=/dls_sw/i08/software/gda/config --restart -v --mode=live logserver &
python /dls_sw/i08/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/i08/software/gda/config --debug -p 8002 --restart -v --mode=live eventserver &
export JAVA_OPTS="-Xms128m -Xmx4096m -XX:MaxPermSize=128m -XX:+DisableExplicitGC"
python /dls_sw/i08/software/gda/workspace_git/gda-core.git/uk.ac.gda.core/bin/gda --smart --trace --config=/dls_sw/i08/software/gda/config --debug -p 8001 --restart -v --mode=live objectserver &