# runs the servers locally
source /dls_sw/dasc/tools_versions/set_tools.sh
umask 0002
/dls_sw/i20/software/gda/plugins/uk.ac.gda.core/bin/gda --config=/dls_sw/i20/software/gda/i20-config --mode=live --debug -p 8001 --restart servers
