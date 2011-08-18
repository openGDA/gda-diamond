# runs the servers locally
source /dls_sw/dasc/tools_versions/set_tools.sh
export JAVA_OPTS=-Xmx2000m
/dls_sw/b18/software/gda/plugins/uk.ac.gda.core/bin/gda --config=/dls_sw/b18/software/gda/config --debug -p 8001 --restart servers
