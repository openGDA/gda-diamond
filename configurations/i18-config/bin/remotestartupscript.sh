source /dls_sw/dasc/tools_versions/set_tools.sh

killall java

JAVA_OPTS="-Xms1024m -Xmx4096m -XX:PermSize=512m -XX:MaxPermSize=1024m" /dls_sw/i18/software/gda_git/gda-core.git/uk.ac.gda.core/bin/gda --config=/dls_sw/i18/software/gda/config --debug -p 8001 --restart servers

