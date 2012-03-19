# runs the servers locally
source /dls_sw/dasc/tools_versions/set_tools.sh
export JAVA_OPTS=-Xmx2000m

/dls_sw/b18/software/gda/plugins/uk.ac.gda.core/bin/gda --stop objectserver
/dls_sw/b18/software/gda/plugins/uk.ac.gda.core/bin/gda --stop eventserver
/dls_sw/b18/software/gda/plugins/uk.ac.gda.core/bin/gda --stop nameserver
JAVA_OPTS="-Xms1024m -Xmx8192m -XX:PermSize=256m -XX:MaxPermSize=512m" /dls_sw/b18/software/gda/plugins/uk.ac.gda.core/bin/gda --config=/dls_sw/b18/software/gda/config --debug -p 8001 --start servers
