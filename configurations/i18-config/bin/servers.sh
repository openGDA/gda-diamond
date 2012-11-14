
# runs the servers locally
source /dls_sw/dasc/tools_versions/set_tools.sh

killall java
#/dls_sw/i18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --stop objectserver
#/dls_sw/i18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --stop eventserver
#/dls_sw/i18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --stop nameserver

#echo "got here"
#touch /dls_sw/i18/software/gda_versions/var/test

#module load java
#whoami > /dls_sw/i18/software/gda_versions/var/test2
JAVA_OPTS="-Xms1024m -Xmx4096m -XX:PermSize=512m -XX:MaxPermSize=1024m" /dls_sw/i18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --config=/dls_sw/i18/software/gda/config --debug -p 8001 --restart servers
